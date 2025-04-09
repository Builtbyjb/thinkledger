package main

import (
	"os"
	"sync"

	"server/cmd/app"
	"server/internal/database/postgres"
	"server/internal/database/redis"
	"server/internal/handlers"
	"server/internal/middleware"

	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"github.com/plaid/plaid-go/plaid"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
)

func init() {
	// Load .env file
	godotenv.Load()
}

func main() {

	// Get gemini api key
	GEMINI_API_KEY := os.Getenv("GEMINI_DEV_API_KEY")

	e := echo.New()

	e.Use(middleware.Cors())
	e.Use(middleware.RequestTimer())
	e.Use(middleware.RateLimiter())
	e.Use(middleware.Recover())

	e.Static("/static", "./static")

	// Create redis client
	redisClient := redis.RedisClient()

	// Create database engine
	db := postgres.DB()

	// Sign in OAuth2 configuration
	signInAuthConfig := &oauth2.Config{
		ClientID:     os.Getenv("GOOGLE_SIGNIN_CLIENT_ID"),
		ClientSecret: os.Getenv("GOOGLE_SIGNIN_CLIENT_SECRET"),
		RedirectURL:  os.Getenv("GOOGLE_SIGNIN_REDIRECT_URL"),
		Scopes: []string{
			"https://www.googleapis.com/auth/userinfo.email",
			"https://www.googleapis.com/auth/userinfo.profile",
		},
		Endpoint: google.Endpoint,
	}

	// Service oauth configuration
	serviceAuthConfig := &oauth2.Config{
		ClientID:     os.Getenv("GOOGLE_SERVICE_CLIENT_ID"),
		ClientSecret: os.Getenv("GOOGLE_SERVICE_CLIENT_SECRET"),
		RedirectURL:  os.Getenv("GOOGLE_SERVICE_REDIRECT_URL"),
		Scopes:       []string{},
		Endpoint:     google.Endpoint,
	}

	// Plaid configuration
	configuration := plaid.NewConfiguration()
	configuration.AddDefaultHeader("PLAID-CLIENT-ID", os.Getenv("PLAID_CLIENT_ID"))
	configuration.AddDefaultHeader("PLAID-SECRET", os.Getenv("PLAID_CLIENT_SECRET"))
	plaidEnv := os.Getenv("PLAID_ENV")

	// Set plaid environment
	if plaidEnv == "sandbox" {
		configuration.UseEnvironment(plaid.Sandbox)
	} else if plaidEnv == "development" {
		configuration.UseEnvironment(plaid.Development)
	} else if plaidEnv == "production" {
		configuration.UseEnvironment(plaid.Production)
	}

	plaidClient := plaid.NewAPIClient(configuration)

	// Dependency injection between routes
	h := &handlers.Handler{
		DB:                db,
		SignInAuthConfig:  signInAuthConfig,
		ServiceAuthConfig: serviceAuthConfig,
		ApiKey:            GEMINI_API_KEY,
		RedisClient:       redisClient,
		PlaidClient:       plaidClient,
	}

	var wg sync.WaitGroup

	wg.Add(2)
	// Handles server function calls
	go func() {
		defer wg.Done()
		app.Server(e, h)
	}()
	// Handles core business logic and background tasks
	go func() {
		defer wg.Done()
		// app.Core(h)
	}()
	wg.Wait()
}
