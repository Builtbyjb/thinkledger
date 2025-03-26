package middleware

import (
	"log"
	"runtime/debug"

	"github.com/labstack/echo/v4"
)

func Recover() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			defer func() {
				if err := recover(); err != nil {
					// c.Logger().Error(err)
					log.Printf(
						"Caught Panice: %v, Stack trace: %s",
						err,
						string(debug.Stack()),
					)
					c.Error(err.(error))
				}
			}()
			return next(c)
		}
	}
}
