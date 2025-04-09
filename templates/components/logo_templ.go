// Code generated by templ - DO NOT EDIT.

// templ: version: v0.3.857
package components

//lint:file-ignore SA4006 This context is only used if a nested component is present.

import "github.com/a-h/templ"
import templruntime "github.com/a-h/templ/runtime"

func Logo() templ.Component {
	return templruntime.GeneratedTemplate(func(templ_7745c5c3_Input templruntime.GeneratedComponentInput) (templ_7745c5c3_Err error) {
		templ_7745c5c3_W, ctx := templ_7745c5c3_Input.Writer, templ_7745c5c3_Input.Context
		if templ_7745c5c3_CtxErr := ctx.Err(); templ_7745c5c3_CtxErr != nil {
			return templ_7745c5c3_CtxErr
		}
		templ_7745c5c3_Buffer, templ_7745c5c3_IsBuffer := templruntime.GetBuffer(templ_7745c5c3_W)
		if !templ_7745c5c3_IsBuffer {
			defer func() {
				templ_7745c5c3_BufErr := templruntime.ReleaseBuffer(templ_7745c5c3_Buffer)
				if templ_7745c5c3_Err == nil {
					templ_7745c5c3_Err = templ_7745c5c3_BufErr
				}
			}()
		}
		ctx = templ.InitializeContext(ctx)
		templ_7745c5c3_Var1 := templ.GetChildren(ctx)
		if templ_7745c5c3_Var1 == nil {
			templ_7745c5c3_Var1 = templ.NopComponent
		}
		ctx = templ.ClearChildren(ctx)
		templ_7745c5c3_Err = templruntime.WriteString(templ_7745c5c3_Buffer, 1, "<div class=\"flex items-center justify-center\"><div class=\"flex h-[1rem] items-center\"><svg viewBox=\"0 0 128 122\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" class=\"w-auto h-full\"><path d=\"M10 0C4.47715 -4.82823e-07 4.82823e-07 4.47715 0 10C-4.82823e-07 15.5228 4.47715 20 10 20L10 0ZM10 20L38.7234 20L38.7234 2.51108e-06L10 0L10 20Z\" fill=\"#0065FA\"></path> <path d=\"M45.689 10H82.1677\" stroke=\"#0065FA\" stroke-width=\"20\"></path> <path d=\"M65.2925 22.0635V48.489\" stroke=\"#0065FA\" stroke-width=\"20\"></path> <path d=\"M55.2925 111.681C55.2925 117.204 59.7696 121.681 65.2925 121.681C70.8153 121.681 75.2925 117.204 75.2925 111.681H55.2925ZM55.2925 56.6758V111.681H75.2925V56.6758H55.2925Z\" fill=\"#0065FA\"></path> <path d=\"M31.2554 10.0718H45.7966H60.3378\" stroke=\"#0065FA\" stroke-width=\"10\"></path> <path d=\"M74.4841 10H89.0254H103.567\" stroke=\"#0065FA\" stroke-width=\"10\"></path> <path d=\"M65.3645 13.0161V27.5573V42.0986\" stroke=\"#0065FA\" stroke-width=\"10\"></path> <path d=\"M65.436 42.1699V56.7111V71.2524\" stroke=\"#0065FA\" stroke-width=\"10\"></path> <path d=\"M118 20C123.523 20 128 15.5228 128 10C128 4.47715 123.523 0 118 0V20ZM89.2766 20H118V0H89.2766V20Z\" fill=\"#0065FA\"></path></svg><h3 class=\"text-xl ms-2\">Thinkledger</h3></div><div class=\"ms-2 h-[1rem]\"><svg viewBox=\"0 0 240 120\" xmlns=\"http://www.w3.org/2000/svg\" class=\"w-auto h-full\"><path d=\"M20 80\n\t\t\t\t L40 40\n\t\t\t\t L80 20\n\t\t\t\t L100 60\n\t\t\t\t L120 100\n\t\t\t\t L140 40\n\t\t\t\t L160 20\n\t\t\t\t L180 70\n\t\t\t\t L200 100\n\t\t\t\t L220 30\" stroke=\"#0065FA\" fill=\"none\" stroke-width=\"15\" stroke-linejoin=\"miter\" stroke-dasharray=\"1000\" stroke-dashoffset=\"1000\"><animate attributeName=\"stroke-dashoffset\" from=\"1000\" to=\"0\" dur=\"1.5s\" fill=\"freeze\" begin=\"0.5s\" calcMode=\"spline\" keySplines=\"0.4 0 0.2 1\" repeatCount=\"indefinite\"></animate></path></svg></div></div>")
		if templ_7745c5c3_Err != nil {
			return templ_7745c5c3_Err
		}
		return nil
	})
}

var _ = templruntime.GeneratedTemplate
