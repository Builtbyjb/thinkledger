package middleware

import (
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"golang.org/x/time/rate"
)

func RateLimiter() echo.MiddlewareFunc {
	return middleware.RateLimiter(
		middleware.NewRateLimiterMemoryStore(
			// 20 requests/sec
			rate.Limit(20),
		),
	)
}
