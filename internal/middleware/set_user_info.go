package middleware

import (
	"fmt"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
)

// Sets userinfo is it exists
func SetUserInfo(r *redis.Client) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()
			var username string

			cookie, err := c.Request().Cookie("authId")
			if err == nil {
				if cookie.Value != "" {
					authId := cookie.Value

					// Get username from redis
					name := fmt.Sprintf("name:%s", authId)
					u, _ := r.Get(ctx, name).Result()
					username = u
				}
			}

			c.Set("username", username)
			return next(c)
		}
	}
}
