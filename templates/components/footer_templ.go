// Code generated by templ - DO NOT EDIT.

// templ: version: v0.3.833
package components

//lint:file-ignore SA4006 This context is only used if a nested component is present.

import "github.com/a-h/templ"
import templruntime "github.com/a-h/templ/runtime"

func Footer() templ.Component {
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
		templ_7745c5c3_Err = templruntime.WriteString(templ_7745c5c3_Buffer, 1, "<footer class=\"mt-24\"><div class=\"grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-8\"><div><h3 class=\"text-lg font-semibold mb-4\">Contact</h3><ul class=\"space-y-2\"><li><a href=\"/support#contact\" class=\"flex hover:text-gray-300\"><i class=\"fa-solid fa-envelope me-2 text-2xl\"></i> Email</a></li></ul></div><div><h3 class=\"text-lg font-semibold mb-4\">Resources</h3><ul class=\"space-y-2\"><li><a href=\"/support\" class=\"hover:text-gray-300\">Support</a></li></ul></div><div><h3 class=\"text-lg font-semibold mb-4\">Legal</h3><ul class=\"space-y-2\"><li><a href=\"/privacy-policy\" class=\"hover:text-gray-300\">Privacy Policy</a></li><li><a href=\"/terms-of-service\" class=\"hover:text-gray-300\">Terms of Service</a></li><li><a href=\"/privacy-policy#cookie-policy\" class=\"hover:text-gray-300 hover:cursor-pointer\">Cookie Policy</a></li></ul></div></div><div class=\"mt-8 pt-8 text-center\"><p class=\"text-sm\">&copy; 2025 ThinkLedger. All rights reserved.</p></div></footer>")
		if templ_7745c5c3_Err != nil {
			return templ_7745c5c3_Err
		}
		return nil
	})
}

var _ = templruntime.GeneratedTemplate
