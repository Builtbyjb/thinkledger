package middleware

import (
	"log"
	"net/http"
	"server/internal/utils"
	"time"

	"github.com/labstack/echo/v4"
)

func AuthRoutes(authConfig utils.AuthConfig) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()

			cookie, err := c.Request().Cookie("user_id")
			if err != nil {
				log.Println(err)
				return c.Redirect(http.StatusTemporaryRedirect, "/sign-in")
			}

			if cookie.Value == "" {
				log.Println("userId cookie is empty")
				return c.Redirect(http.StatusTemporaryRedirect, "/sign-in")
			}
			userId := cookie.Value

			// Get token from token store
			token, err := authConfig.TokenStore.GetToken(userId)
			if err != nil {
				log.Println(err)
				return c.Redirect(http.StatusTemporaryRedirect, "/sign-in")
			}

			// Check if the token as expired and try refreshing if there is a refresh token
			if token.Expiry.Before(time.Now()) {

				if token.RefreshToken == "" {
					log.Println("Token has expired and no refresh token is available")
					return c.Redirect(http.StatusTemporaryRedirect, "/sign-in")
				}

				// Try refreshing the token
				newToken, err := authConfig.OAuth2Config.TokenSource(ctx, token).Token()
				if err != nil {
					log.Println(err)
					return c.Redirect(http.StatusTemporaryRedirect, "/sign-in")
				}

				// Save the new token
				token = newToken
				if err := authConfig.TokenStore.SaveToken(userId, token); err != nil {
					return c.JSON(http.StatusInternalServerError, map[string]string{
						"error": "Failed to save refreshed token",
					})
				}
			}

			// Verify the token with google
			isValid := verifyToken(token.AccessToken)
			if !isValid {
				log.Println("Access token is not valid")
				return c.Redirect(http.StatusTemporaryRedirect, "/sign-in")
			}

			// Token is valid, store it in context for handlers to use
			c.Set("userToken", token)
			c.Set("userId", userId)
			return next(c)
		}
	}
}

func verifyToken(accessToken string) bool {
	client := &http.Client{Timeout: 10 * time.Second}
	tokenInfoURL := "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=" + accessToken

	response, err := client.Get(tokenInfoURL)
	if err != nil {
		log.Println("Token response error")
		return false
	}
	defer response.Body.Close()

	// Response status code would be 200 if the token is valid
	if response.StatusCode != 200 {
		log.Println("Token response status code error")
		return false
	}

	return true
}
