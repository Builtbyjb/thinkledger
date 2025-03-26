package middleware

import (
	"context"
	"fmt"
	"time"

	"github.com/labstack/echo/v4"
)

func RequestTimer() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			start := time.Now()
			path := c.Path()
			method := c.Request().Method

			defer func() {
				duration := time.Since(start)
				status := c.Response().Status
				ctxErr := c.Request().Context().Err()

				if ctxErr == context.Canceled && status == 0 {
					fmt.Printf(
						"method=%s path=%s duration=%s status=aborted\n",
						method, path, duration,
					)
				} else {
					fmt.Printf(
						"method=%s path=%s duration=%s status=%d\n",
						method, path, duration, status,
					)
				}
			}()

			return next(c)
		}
	}
}
