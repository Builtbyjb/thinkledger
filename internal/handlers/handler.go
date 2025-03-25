package handlers

import (
	"server/internal/utils"

	"github.com/a-h/templ"
	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
	"gorm.io/gorm"
)

// Dependency injection between routes
type Handler struct {
	DB          *gorm.DB
	ApiKey      string
	OAuthConfig *oauth2.Config
	TokenStore  utils.TokenStore
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
