package middleware

import (
	"log"
	"server/internal/utils"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"golang.org/x/oauth2"
	"gorm.io/gorm"
)

func RouteAuth(
	redisClient *redis.Client,
	signInAuthConfig *oauth2.Config,
	db *gorm.DB,
) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()

			cookie, err := c.Request().Cookie("session_id")
			if err != nil || cookie.Value == "" {
				log.Println(err)
				return c.Redirect(307, "/sign-in")
			}

			sessionID := cookie.Value

			// Get userID
			userID, err := redisClient.Get(ctx, sessionID).Result()
			if err != nil {
				log.Printf("Error getting userID: %s", err)
				return c.Redirect(307, "/sign-in")
			}

			// Get token from redis
			userToken := "signInAccessToken:" + userID
			accessToken, err := redisClient.Get(ctx, userToken).Result()
			if err != nil {
				log.Printf("Error getting access token: %s", err)
				return c.Redirect(307, "/sign-in")
			}

			/*
				write logic that alerts the user for a refresh token, if the
				refresh token as expired and pause all operations on the users account
			*/

			isValid, err := utils.VerifyGoogleAccessToken(accessToken)
			if !isValid {
				log.Println(err)

				token, err := utils.GetUserSignInToken(redisClient, userID)
				if err != nil {
					log.Println(err)
					c.Redirect(307, "/sign-in")
				}

				// Try refreshing the token
				newToken, err := utils.RefreshGoogleToken(token, signInAuthConfig)
				if err != nil {
					utils.ClearSessionIDCookie(c)
					log.Println(err)
					return c.Redirect(307, "/sign-in")

				} else {
					// Save new token
					if err := utils.SaveUserSignInToken(redisClient, newToken, userID); err != nil {
						log.Println(err)
						return c.Redirect(307, "/sign-in")
					}

					// Save new access token
					userToken := "token:" + userID
					if err := redisClient.Set(ctx, userToken, newToken.AccessToken, 0).Err(); err != nil {
						log.Println(err)
						return c.String(500, "Failed to save token: "+err.Error())
					}
				}
			}

			// Get username
			username := "username:" + userID
			name, err := redisClient.Get(ctx, username).Result()
			if err != nil {
				log.Printf("Error getting user username: %s", err)
				return c.Redirect(307, "/sign-in")
			}

			// Token is valid, store it in context for handlers to use
			// c.Set("userToken", token)
			// c.Set("authId", authId)
			c.Set("username", name)
			c.Set("userID", userID)
			return next(c)
		}
	}
}

// Sets userinfo is it exists
func SetUserInfo(r *redis.Client) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()
			var name string

			cookie, err := c.Request().Cookie("session_id")
			if err == nil {
				if cookie.Value != "" {
					sessionID := cookie.Value
					userID, _ := r.Get(ctx, sessionID).Result()

					// Get user info from redis
					username := "username:" + userID
					u, _ := r.Get(ctx, username).Result()
					name = u
				}
			}

			c.Set("username", name)
			return next(c)
		}
	}
}
