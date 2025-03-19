package middleware

import (
	"context"
	"fmt"
	"time"

	"github.com/gofiber/fiber/v2"
)

func RequestTimer() fiber.Handler {
	return func(c *fiber.Ctx) error {
		start := time.Now()
		path := c.Path()
		method := c.Method()

		defer func() {
			duration := time.Since(start)
			status := c.Response().StatusCode()
			ctxErr := c.Context().Err()

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

		return c.Next()
	}
}
