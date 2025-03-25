package handlers

import (
	"log"
	"net/http"
	"server/internal/utils"
	"time"

	"github.com/labstack/echo/v4"
)

func (h *Handler) HandleSignInAuth(c echo.Context) error {
	state, err := utils.GenerateRandomstring()
	if err != nil {
		log.Println(err)
		return c.String(
			http.StatusInternalServerError,
			"Internal server error",
		)
	}

	// Set state cookie
	c.SetCookie(&http.Cookie{
		Name:     "state",
		Value:    state,
		HttpOnly: true,
		Path:     "/",
		Secure:   true,
		Expires:  time.Now().Add(10 * time.Minute),
	})

	// Add oauth2.AccessTypeOffline to get a refresh token
	return c.Redirect(
		http.StatusTemporaryRedirect,
		h.OAuthConfig.AuthCodeURL(state),
	)
}
