package app

import (
	"os"
	"server/internal/handlers"
	"server/internal/middleware"

	"github.com/labstack/echo/v4"
)

func Server(e *echo.Echo, h *handlers.Handler) {

	// health check
	e.GET("/ping", func(c echo.Context) error {
		envCheck := os.Getenv("ENV_CHECK")

		return c.JSON(200, map[string]string{
			"ping": "pong!!",
			"env":  envCheck,
		})
	})

	// Web routes
	e.GET("/", h.Index)

	// Routes that appear when a user is authenticated and unauthenticated
	d := e.Group("", middleware.SetUserInfo(h.RedisClient))
	d.GET("/support", h.Support)
	d.GET("/support/bookkeeping", h.SupportBookkeeping)
	d.GET("/support/financial-reports", h.SupportFinancialReports)
	d.GET("/support/analytics-insights", h.SupportAnalyticsInsights)
	d.GET("/privacy-policy", h.PrivacyPolicy)
	d.GET("/terms-of-service", h.TermsOfService)

	e.POST("/join-waitlist", h.JoinWaitlist)

	e.GET("/sign-out", h.Signout)

	// Authentication routes
	e.GET("/auth-sign-in", h.SignInAuth)
	e.GET("/auth/google/callback/sign-in", h.GoogleSignInCallback)
	e.GET("/auth/google/callback/services", h.GoogleServiceCallback)

	// Protected web routes
	p := e.Group("", middleware.RouteAuth(h.RedisClient, h.SignInAuthConfig, h.DB))
	p.GET("/home", h.Home)
	p.GET("/banking", h.Banking)
	p.GET("/google", h.Google)
	p.GET("/plaid-link-token", h.PlaidLinkToken)
	p.POST("/plaid-access-token", h.PlaidAccessToken)
	p.GET("/auth-google-service", h.GoogleServiceToken)

	e.POST("/plaid-webhooks", h.PlaidWebhooks)
	e.GET("auth/plaid/callback", h.PlaidCallback)

	// Not found (404) handler
	e.GET("*", h.NotFound)

	// Api routes
	// v1 := app.Group("/api/v1")
	// v1.POST("/chat", handler.HandleChat)

	// api.Get("/journal", handler.HandleJournal)
	// api.Get("/t-accounts", handler.HandleTAccount)
	// api.Get("/trial-balance", handler.HandleTrialBalance)

	e.Logger.Fatal(e.Start(":3000"))
}
