class mde extends HTMLElement { // create new elem
    constructor() {
        super();
        mde.prototype.show = function(){
            this.style.display = "block"
        }
        mde.prototype.hide = function(){
            this.style.display = "none"
        }
        /*mde.prototype.destroy = function(public, private) {
            if (htmlp.security.internal.verify(public , private)) {
                this.remove()
            }
        }*/
    }
    connectedCallback(){
        this.setAttribute('class', 'modal')
        if (this.hasAttribute("dontCloseOnClickOutside")){return}
        this.addEventListener("click", function(e){
            if (e.target.tagName.toLowerCase() == "htmlp-modal") {this.style.display = 'none'}
        });
        const close_btn = document.createElement('span')
        close_btn.innerHTML = "&times;" 
        close_btn.setAttribute('class', 'mde-close')
        close_btn.setAttribute('id', 'htmlp_modalClose')
        if (!this.hasAttribute('noclosebtn')) {
            this.appendChild(close_btn)
            close_btn.addEventListener('click', function(){
                this.parentElement.hide()
            });
        }
            //this.parentElement.firstChild.appendChild(close_btn)
       document.addEventListener("DOMContentLoaded", function(){
        document.getElementById("htmlp_modalClose").addEventListener('click', function(){
            if (this.parentElement.parentElement.tagName.toLowerCase() == "htmlp-modal") {
                this.parentElement.parentElement.style.display = "none"
            } else if (this.parentElement.parentElement.parentElement.tagName.toLowerCase() == "htmlp-modal") {
                this.parentElement.parentElement.parentElement.style.display = "none"
            } else if (this.parentElement.parentElement.parentElement.parentElement.tagName.toLowerCase()=="htmlp-modal") {
                this.parentElement.parentElement.parentElement.parentElement.style.display = "none"
            }
        })
       })
    }
}
class aac extends HTMLElement {
    constructor(){
        super()
    }
    connectedCallback(){
        this.setAttribute('style', 'position:absolute;left:50%;top:50%;')
    } 
    disconnectedCallback(){
        if (this.hasAttribute('style')) { // good practice
        this.setAttribute('style', this.getAttribute('style').toString().replace('position:absolute;left:50%;top:50%;', ''))
        }
    }
}
htmlp = function(){
    console.debug("HTML Plus, Main function. Use htmlp.help() For help & guides.")
}

htmlp.help = function(){
    console.warn("Help is on it's way! (not implemented yet)")
}
htmlp.define = function(){
    console.debug("Used to define elements, like htmlp.define.mde() would define and allow use of Modal Easy. Use htmlp.define.all() to define all elements.")
}
htmlp.define.mde = function(){
    customElements.define("htmlp-modal", mde)
}
htmlp.define.aac = function(){
    customElements.define('htmlp-aac', aac)
}
htmlp.define.all = function(){
    htmlp.define.mde()
    htmlp.define.aac()
}
htmlp.help = function(){
    console.debug("Usage and docs can be viewed here: freewebutilities.pythonanywhere.com/dev/htmlp")
    console.debug("Help function will be truly implemented soon!")
}
htmlp.global = function(){
    console.debug("Global Functions & Prototypes")
}
htmlp.global.hide = function(){
    HTMLHtmlElement.prototype.hide = function(){
        try {
            document.getElementsByTagName('html')[0].show()
        } catch (e) {
            console.warn("My not be able to show document again, as Document.show() is not defined. Run htmlp.global.show() to allow this to happen. Error logged in console.")
            console.error(e)
        }
        document.body.setAttribute('style', "display:none;")
    }
    document.hide = function(){
        try {
            document.getElementsByTagName('html')[0].show()
        } catch (e) {
            console.warn("My not be able to show document again, as Document.show() is not defined. Run htmlp.global.show() to allow this to happen. Error logged in console.")
            console.error(e)
        }
        document.body.setAttribute('style', "display:none;")
    }
}
htmlp.global.show = function(){
    HTMLHtmlElement.prototype.show = function(){
        document.body.setAttribute('style', "display:block;")
    }
    document.show = function(){
        document.body.setAttribute('style', "display:block;")
    }
} 
htmlp.internal = function(){
    console.log("internal functions, only use htmlp.internal.loadjQuery() to load jQuery when necessary!")
}
htmlp.internal.loadjQuery = function(){
    try { // check for jQuery and make a new script if it is not loaded.
        $(document).ready(function(){
            console.log('jQuery has already been loaded!')
        });
    } catch(e){
        console.warn("jQuery may not be loaded, or $(document).ready() is not accessible. Creating a jQuery Script (CDN)...")
        const new_jquery = document.createElement("script")
        console.error("Error: \n"+e)
        new_jquery.src = "https://code.jquery.com/jquery-3.6.0.min.js"
        document.head.appendChild(new_jquery)
        console.debug("Created a new jQuery Script!")
        console.debug("Trying Again... to verify it loaded correctly")
        document.addEventListener('load', function(){
            try {
                $(document).ready(function(){
                    console.log('jQuery Loaded successfully!')
                });
            } catch(e){
                console.error(e)
                console.debug("ERROR, jQuery could not be accessed!")
            } finally {
                console.debug('IF no errors occurred, jQuery was successfully loaded!')
            }
        })
    }
}
// Security Management
/* 
htmlp.security = function() {
    console.debug('Security Functions. DO NOT USE FOR ANYTHING EXTREMELY IMPORTANT, EG: PASSWORDS')
}
htmlp.security.keys = function() {
    console.debug('Security Key Management')
}
htmlp.security.keys.internal = function() {
    console.warn('Internal Security Functions. DO NOT CALL THESE FUNCTIONS')
}
htmlp.security.keys.generate() = function() {
    const private = Math.floor(Math.random() *1000000000)
    const public = 5(private * private)/3.14159*500
    return public
}
htmlp.security.keys.generate.getPrivate = function(public) {
    return 5/(public/public)/3.14159/500
}
htmlp.security.internal.verify = function(publicKey, privateKey) {
    const private = privateKey
    const public = 5(private * private)/3.14159*500
    if (public === publicKey) {
        return true
    } else {
        return false
    }
}
*/