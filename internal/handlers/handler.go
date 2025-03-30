package handlers

import (
	"github.com/a-h/templ"
	"github.com/labstack/echo/v4"
	"github.com/plaid/plaid-go/plaid"
	"github.com/redis/go-redis/v9"
	"golang.org/x/oauth2"
	"gorm.io/gorm"
)

// Dependency injection between routes
type Handler struct {
	DB          *gorm.DB
	ApiKey      string
	OAuthConfig *oauth2.Config
	RedisClient *redis.Client
	PlaidClient *plaid.APIClient
}

// Renders templ templates
func Render(ctx echo.Context, statusCode int, t templ.Component) error {
	buf := templ.GetBuffer()
	defer templ.ReleaseBuffer(buf)

	if err := t.Render(ctx.Request().Context(), buf); err != nil {
		return err
	}

	return ctx.HTML(statusCode, buf.String())
}
