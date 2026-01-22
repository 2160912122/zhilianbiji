// jsmind.undo.js
(function(){
    if(!window.jsMind) throw new Error('jsMind is not defined');
    var jm = window.jsMind;
    jm.undo = function(jm){
        this.jm = jm;
        this.stack = [];
        this.index = -1;
        this.max_stack_size = 100;
        this.init();
    };
    jm.undo.prototype = {
        init: function(){
            this.jm.add_event_listener(this.event_handler.bind(this));
            // 绑定快捷键
            var self = this;
            document.addEventListener('keydown', function(e){
                if((e.ctrlKey || e.metaKey) && !e.altKey){
                    if(e.keyCode === 90){ // Ctrl+Z
                        if(e.shiftKey) self.redo();
                        else self.undo();
                        e.preventDefault();
                    }else if(e.keyCode === 89){ // Ctrl+Y
                        self.redo();
                        e.preventDefault();
                    }
                }
            });
        },
        event_handler: function(type, data){
            if(type === 'edit' || type === 'add_node' || type === 'remove_node' || 
               type === 'move_node' || type === 'resize'){
                this.push_snapshot();
            }
        },
        push_snapshot: function(){
            // 移除当前索引之后的所有记录
            this.stack = this.stack.slice(0, this.index + 1);
            // 添加新快照
            var snapshot = this.jm.get_data();
            this.stack.push(snapshot);
            // 限制栈大小
            if(this.stack.length > this.max_stack_size){
                this.stack.shift();
            }
            this.index = this.stack.length - 1;
        },
        undo: function(){
            if(this.index <= 0) return;
            this.index--;
            var snapshot = this.stack[this.index];
            this.jm.show(snapshot);
        },
        redo: function(){
            if(this.index >= this.stack.length - 1) return;
            this.index++;
            var snapshot = this.stack[this.index];
            this.jm.show(snapshot);
        },
        clear: function(){
            this.stack = [];
            this.index = -1;
        }
    };
    jm.plugin.undo = jm.undo;
})();