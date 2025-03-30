package middleware

import (
	"encoding/json"
	"log"
	"server/internal/utils"

	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
)

func AuthRoutes(authConfig utils.AuthConfig) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()

			cookie, err := c.Request().Cookie("session_id")
			if err != nil {
				log.Println(err)
				return c.Redirect(307, "/sign-in")
			}

			if cookie.Value == "" {
				log.Println("session id cookie is empty")
				return c.Redirect(307, "/sign-in")
			}
			sessionID := cookie.Value

			// Get token from redis
			tokenStr, err := authConfig.RedisClient.Get(ctx, sessionID).Result()
			if err != nil {
				log.Printf("Error getting token bytes: %s", err)
				return c.Redirect(307, "/sign-in")
			}

			// Deserialize token to JSON
			var token *oauth2.Token
			if err := json.Unmarshal([]byte(tokenStr), &token); err != nil {
				log.Println(err)
				return c.Redirect(307, "/sign-in")
			}

			/*
				write logic that alerts the user for a refresh token, if the refresh token
				as expired and pause all operations on the users account
			*/
			verifedToken, err := utils.VerifyGoogleToken(token, authConfig.OAuth2Config)
			if err != nil {
				utils.ClearSessionIDCookie(c)
				log.Println(err)
				return c.Redirect(307, "/sign-in")
			}

			verifiedTokenBytes, err := json.Marshal(verifedToken)
			if err != nil {
				log.Println(err)
				return c.String(500, "Failed to marshal token: "+err.Error())
			}

			// Save the new verified token
			if err := authConfig.RedisClient.Set(ctx, sessionID, verifiedTokenBytes, 0).Err(); err != nil {
				log.Printf("Error saving new verified token: %s", err)
				return c.String(500, "Failed to save token: "+err.Error())
			}

			// Get user info from redis
			sessionUser := "user:" + sessionID
			userInfoStr, err := authConfig.RedisClient.Get(ctx, sessionUser).Result()
			if err != nil {
				log.Printf("Error getting user bytes: %s", err)
				return c.Redirect(307, "/sign-in")
			}

			// Deserialize user info to JSON
			var userInfo *utils.UserInfo
			if err := json.Unmarshal([]byte(userInfoStr), &userInfo); err != nil {
				log.Println(err)
				return c.Redirect(307, "/sign-in")
			}

			// Token is valid, store it in context for handlers to use
			// c.Set("userToken", token)
			// c.Set("authId", authId)
			c.Set("username", userInfo.Name)
			return next(c)
		}
	}
}
