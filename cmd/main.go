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

	// Postgres credentials
	POSTGRES_DB := os.Getenv("POSTGRES_DB")
	POSTGRES_USER := os.Getenv("POSTGRES_USER")
	POSTGRES_PASSWORD := os.Getenv("POSTGRES_PASSWORD")
	POSTGRES_HOST := os.Getenv("POSTGRES_HOST")
	POSTGRES_PORT := os.Getenv("POSTGRES_PORT")

	app := fiber.New()

	app.Use(
		middleware.Cors(),
		middleware.RequestTimer(),
		middleware.RateLimiter(),
	)

	// Connect to database and create database engine
	db := database.DB(
		POSTGRES_DB,
		POSTGRES_USER,
		POSTGRES_PASSWORD,
		POSTGRES_HOST,
		POSTGRES_PORT,
	)

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

	// Protected routes group
	// api := app.Group("/api", middleware.AuthMiddleware())
	api := app.Group("/api")
	api.Post("/chat", handler.HandleChat)
	api.Get("/journal", handler.HandleJournal)
	api.Get("/t-accounts", handler.HandleTAccount)
	api.Get("/trial-balance", handler.HandleTrialBalance)

	log.Fatal(app.Listen("0.0.0.0:3000"))
}
