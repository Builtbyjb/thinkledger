package main

import (
	"log"
	"os"

	"server/database"
	"server/handlers"
	"server/middleware"

	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
)

func main() {

	// Load .env file
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Error loading .env file")
	}

	// Get gemini api key
	GEMINI_API_KEY := os.Getenv("GEMINI_DEV_API_KEY")

	app := fiber.New()

	app.Use(
		middleware.Cors(),
		middleware.RateLimiter(),
		middleware.RequestTimer(),
	)

	// Connect to database and create database engine
	db := database.DB()

	handler := &handlers.Handler{
		DB:     db,
		ApiKey: GEMINI_API_KEY,
	}

	// health check
	app.Get("/ping", func(c *fiber.Ctx) error {
		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"ping": "pong!",
		})
	})

	api := app.Group("/api", middleware.AuthMiddleware())
	api.Post("/chat", handler.HandleChat)
	// api.Get("/journal", handler.HandleJournal)
	// api.Get("/t-accounts", handler.HandleTAccount)
	// api.Get("/trial-balance", handler.HandleTrialBalance)

	log.Fatal(app.Listen("0.0.0.0:3000"))
}
