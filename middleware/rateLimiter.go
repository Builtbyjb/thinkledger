package middleware

import (
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/limiter"
)

func RateLimiter() fiber.Handler {
	return limiter.New(limiter.Config{
		// Skips requests from localhost
		Next: func(c *fiber.Ctx) bool {
			return c.IP() == "127.0.0.1"
		},
		// Allows 20 requests in 30 seconds
		Max:        20,
		Expiration: 30 * time.Second,
		KeyGenerator: func(c *fiber.Ctx) string {
			return c.Get("x-forwarded-for")
		},
		LimitReached: func(c *fiber.Ctx) error {
			return c.Status(fiber.StatusTooManyRequests).SendString("Too many requests!!")
		},
		LimiterMiddleware: limiter.SlidingWindow{},
		// TODO: use redis to store requests
		// Storage: myCustomStorage{},
	})
}
