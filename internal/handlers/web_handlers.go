package handlers

import (
	"server/templates"
	"server/templates/guest"

	"github.com/gofiber/fiber/v2"
)

func (h *Handler) Index(c *fiber.Ctx) error {
	return Render(c, guest.IndexPage())
}

func (h *Handler) Support(c *fiber.Ctx) error {
	return Render(c, guest.SupportPage())
}

func (h *Handler) SupportBookkeeping(c *fiber.Ctx) error {
	return Render(c, guest.SupportBookkeepingPage())
}

func (h *Handler) SupportFinancialReports(c *fiber.Ctx) error {
	return Render(c, guest.SupportFinancialReportsPage())
}

func (h *Handler) SupportAnalyticsInsights(c *fiber.Ctx) error {
	return Render(c, guest.SupportAnalyticsInsightsPage())
}

func (h *Handler) PrivacyPolicy(c *fiber.Ctx) error {
	return Render(c, guest.PrivacyPolicyPage())
}

func (h *Handler) TermsOfService(c *fiber.Ctx) error {
	return Render(c, guest.TermsOfServicePage())
}

func (h *Handler) NotFound(c *fiber.Ctx) error {
	return Render(c, templates.NotFoundPage())
}
