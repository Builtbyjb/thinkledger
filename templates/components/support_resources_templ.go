// Code generated by templ - DO NOT EDIT.

// templ: version: v0.3.833
package components

//lint:file-ignore SA4006 This context is only used if a nested component is present.

import "github.com/a-h/templ"
import templruntime "github.com/a-h/templ/runtime"

func SupportResources() templ.Component {
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
		templ_7745c5c3_Err = templruntime.WriteString(templ_7745c5c3_Buffer, 1, "<h2 class=\"text-2xl font-medium mb-8\">Resources</h2><div class=\"grid sm:grid-cols-2 lg:grid-cols-2 gap-6\"><a href=\"\" class=\"group\"><div class=\"p-4 h-full\"><div class=\"font-medium text-xl mb-4\">Getting Started Guide</div><div class=\"mb-4\">Learn the basics and set up your account</div><div class=\"flex items-center\"><span>Read guide</span></div></div></a> <a href=\"/resources/tutorials\" class=\"group\"><div class=\"p-4 h-full\"><div class=\"font-medium mb-4 text-xl\">Video Tutorials</div><div class=\"mb-4\">Watch step-by-step tutorials on using our features</div><div class=\"flex items-center\"><span>Watch videos</span></div></div></a> <a href=\"/resources/api\" class=\"group\"><div class=\"bg-background p-6 rounded-lg border hover:border-primary transition-colors\"><h3 class=\"font-medium mb-2 group-hover:text-primary transition-colors\">API Documentation</h3><p class=\"text-sm text-muted-foreground mb-4\">Integrate AI Accountant with your existing systems</p><div class=\"flex items-center text-sm text-primary\"><span>View docs</span></div></div></a></div>")
		if templ_7745c5c3_Err != nil {
			return templ_7745c5c3_Err
		}
		return nil
	})
}

var _ = templruntime.GeneratedTemplate
