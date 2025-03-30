package middleware

import (
	"encoding/json"
	"fmt"
	"server/internal/utils"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
)

// Sets userinfo is it exists
func SetUserInfo(r *redis.Client) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()
			var userInfo utils.UserInfo

			cookie, err := c.Request().Cookie("session_id")
			if err == nil {
				if cookie.Value != "" {
					sessionID := cookie.Value

					// Get user info from redis
					sessionUser := fmt.Sprintf("user:%s", sessionID)
					u, _ := r.Get(ctx, sessionUser).Result()
					_ = json.Unmarshal([]byte(u), &userInfo)
				}
			}

			c.Set("username", userInfo.Name)
			return next(c)
		}
	}
}
