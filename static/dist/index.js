(function(){function a(){b(),d.forEach(a=>{a.classList.remove("hidden")}),e.forEach(a=>{a.classList.add("hidden")})}function b(){const a=document.querySelectorAll("#lastname");a.forEach(a=>{a.value=""});const b=document.querySelectorAll("#firstname");b.forEach(a=>{a.value=""});const c=document.querySelectorAll("#email");c.forEach(a=>{a.value=""})}async function c(b){try{const c=await fetch("/join-waitlist",{method:"POST",body:b});200===c.status?(alert("You've been added to the waitlist! A welcome email has been sent to you. If you don't see it in your inbox, please check your spam folder. Thank you!"),a()):400===c.status&&alert(" Please provide valid credentials")}catch(a){console.log(a)}}const d=document.querySelectorAll("#display-join-waitlist-form"),e=document.querySelectorAll("#join-waitlist-form"),f=document.querySelectorAll("#close-join-waitlist-form");d.forEach(a=>{a.addEventListener("click",()=>{a.classList.add("hidden"),e.forEach(a=>{a.classList.remove("hidden")})})}),f.forEach(b=>{b.addEventListener("click",()=>{a()})}),document.addEventListener("submit",async a=>{a.preventDefault();const b=a.target.id;if("join-waitlist-submit"===b){const b=a.target.firstname.value,d=a.target.lastname.value,e=a.target.email.value,f=new FormData;f.append("firstname",b),f.append("lastname",d),f.append("email",e),await c(f)}})})();