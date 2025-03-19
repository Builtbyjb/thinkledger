package handlers

import (
	"github.com/a-h/templ"
	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

// To pass database engine between api endpoints
type Handler struct {
	DB     *gorm.DB
	ApiKey string
}

// Renders templ templates
func Render(c *fiber.Ctx, component templ.Component) error {
	c.Set("Content-Type", "text/html")
	return component.Render(c.Context(), c.Response().BodyWriter())
}
