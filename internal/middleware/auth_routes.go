package middleware

import (
	"encoding/json"
	"log"
	"net/http"
	"server/internal/utils"
	"time"

	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
)

func AuthRoutes(authConfig utils.AuthConfig) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()

			cookie, err := c.Request().Cookie("authId")
			if err != nil {
				log.Println(err)
				return c.Redirect(307, "/sign-in")
			}

			if cookie.Value == "" {
				log.Println("authId cookie is empty")
				return c.Redirect(307, "/sign-in")
			}
			authId := cookie.Value

			// Get token from token store
			tokenStr, err := authConfig.RedisClient.Get(ctx, authId).Result()
			if err != nil {
				log.Println(err)
				return c.Redirect(307, "/sign-in")
			}

			// Deserialize the token from JSON
			var token *oauth2.Token
			if err := json.Unmarshal([]byte(tokenStr), &token); err != nil {
				log.Println("Failed to unmarshal token:", err)
				return c.Redirect(307, "/sign-in")
			}

			// Check if the token as expired and try refreshing if there is a refresh token
			if token.Expiry.Before(time.Now()) {

				if token.RefreshToken == "" {
					log.Println("Token has expired and no refresh token is available")
					return c.Redirect(307, "/sign-in")
				}

				// Try refreshing the token
				newToken, err := authConfig.OAuth2Config.TokenSource(ctx, token).Token()
				if err != nil {
					log.Println(err)
					return c.Redirect(307, "/sign-in")
				}

				// Save the new token
				token = newToken
				if err := authConfig.RedisClient.Set(ctx, authId, token, 0).Err(); err != nil {
					log.Println(err)
					return c.JSON(500, map[string]string{
						"error": "Failed to save refreshed token",
					})
				}
			}

			// Verify the token with google
			isValid := verifyToken(token.AccessToken)
			if !isValid {
				log.Println("Access token is not valid")
				return c.Redirect(307, "/sign-in")
			}

			// Token is valid, store it in context for handlers to use
			c.Set("userToken", token)
			c.Set("authId", authId)
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
