package middleware

import (
	"context"
	"log"
	"os"
	"strings"

	"github.com/gofiber/fiber/v2"
	"google.golang.org/api/idtoken"
)

func GoogleChatAuth() fiber.Handler {
	return func(c *fiber.Ctx) error {
		authHeader := c.Get("Authorization")
		if authHeader == "" {
			log.Println("missing authorization header")
			return c.Status(fiber.StatusUnauthorized).
				SendString("Missing Authorization header")
		}

		token := strings.TrimPrefix(authHeader, "Bearer ")
		// log.Println(token)

		tokenAudience := os.Getenv("GOOGLE_CHAT_AUDIENCE")

		// Validate token
		payload, err := idtoken.Validate(context.Background(), token, tokenAudience)
		if err != nil {
			log.Println("invalid jwt")
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"error": "Invalid JWT: " + err.Error(),
			})
		}

		// Verify issuer
		if payload.Issuer != "https://accounts.google.com" &&
			payload.Issuer != "accounts.google.com" {
			log.Println("invalid issuer")
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"error": "Invalid issuer",
			})
		}

		// Store verified claims in context
		c.Locals("googleClaims", payload)
		return c.Next()
	}
}
