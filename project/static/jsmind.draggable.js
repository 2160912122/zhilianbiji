/*!
 * jsMind.draggable.js 0.4.6
 * https://github.com/hizzgdev/jsmind/
 */
(function (jsMind) {
    'use strict';

    if (!jsMind) {
        return;
    }

    var $d = document;
    var $c = $d.createElement('canvas');
    var _canvas_ctx = $c.getContext('2d');

    var _default_opts = {
        line_width: 2,
        line_color: '#555',
        drag_highlight: '#ffd700'
    };

    var _opts = {};
    var _jm = null;
    var _selected_node = null;
    var _dragging = false;
    var _drag_start = false;
    var _drag_target = null;
    var _drag_image = null;
    var _drag_x = 0;
    var _drag_y = 0;
    var _view = null;

    function jm_draggable(jm, options) {
        if (!jm) {
            throw new Error('invalid jm');
        }
        _jm = jm;
        _opts = jsMind.util.merge(_default_opts, options);
        _view = _jm.view;
        _init_draggable();
    }

    function _init_draggable() {
        var c = _jm.view.getCanvas();
        c.addEventListener('mousedown', _handle_mousedown);
        c.addEventListener('mousemove', _handle_mousemove);
        c.addEventListener('mouseup', _handle_mouseup);
        c.addEventListener('touchstart', _handle_touchstart);
        c.addEventListener('touchmove', _handle_touchmove);
        c.addEventListener('touchend', _handle_touchend);
    }

    function _handle_mousedown(e) {
        if (_dragging) {
            return;
        }
        var jmn = _get_node(e);
        if (!!jmn && _jm.is_editable()) {
            _selected_node = jmn;
            _drag_start = true;
            _drag_x = e.clientX;
            _drag_y = e.clientY;
            e.stopPropagation();
        }
    }

    function _handle_mousemove(e) {
        if (_drag_start) {
            var dx = e.clientX - _drag_x;
            var dy = e.clientY - _drag_y;
            var distance = Math.sqrt(dx * dx + dy * dy);
            if (distance > 5) {
                _start_drag(e);
                _drag_start = false;
            }
        }
        if (_dragging) {
            _do_drag(e);
            e.preventDefault();
        }
    }

    function _handle_mouseup(e) {
        if (_dragging) {
            _stop_drag(e);
            e.preventDefault();
        }
        _drag_start = false;
    }

    function _handle_touchstart(e) {
        if (_dragging) {
            return;
        }
        var jmn = _get_node(e);
        if (!!jmn && _jm.is_editable()) {
            _selected_node = jmn;
            _drag_start = true;
            var touch = e.touches[0];
            _drag_x = touch.clientX;
            _drag_y = touch.clientY;
            e.stopPropagation();
            e.preventDefault();
        }
    }

    function _handle_touchmove(e) {
        if (_drag_start) {
            var touch = e.touches[0];
            var dx = touch.clientX - _drag_x;
            var dy = touch.clientY - _drag_y;
            var distance = Math.sqrt(dx * dx + dy * dy);
            if (distance > 5) {
                _start_drag(e);
                _drag_start = false;
            }
        }
        if (_dragging) {
            _do_drag(e);
            e.preventDefault();
        }
    }

    function _handle_touchend(e) {
        if (_dragging) {
            _stop_drag(e);
            e.preventDefault();
        }
        _drag_start = false;
    }

    function _get_node(e) {
        var element = null;
        if (e.type.indexOf('touch') >= 0) {
            if (e.touches.length > 0) {
                element = _view.elementFromPoint(e.touches[0].clientX, e.touches[0].clientY);
            }
        } else {
            element = e.target;
        }
        return _jm.get_node(element);
    }

    function _start_drag(e) {
        _dragging = true;
        _drag_target = _selected_node;
        _create_drag_image();
        _view.show_drag_line(_drag_target, _opts.drag_highlight);
        _jm.invoke_event_handlers('dragstart', { node: _drag_target, event: e });
    }

    function _do_drag(e) {
        var x = 0, y = 0;
        if (e.type.indexOf('touch') >= 0) {
            if (e.touches.length > 0) {
                x = e.touches[0].clientX;
                y = e.touches[0].clientY;
            }
        } else {
            x = e.clientX;
            y = e.clientY;
        }
        _update_drag_image(x, y);
        var target_node = _view.get_drop_target(x, y);
        _view.update_drag_line(_drag_target, target_node);
        _jm.invoke_event_handlers('drag', { node: _drag_target, event: e });
    }

    function _stop_drag(e) {
        _dragging = false;
        var x = 0, y = 0;
        if (e.type.indexOf('touch') >= 0) {
            if (e.changedTouches.length > 0) {
                x = e.changedTouches[0].clientX;
                y = e.changedTouches[0].clientY;
            }
        } else {
            x = e.clientX;
            y = e.clientY;
        }
        var target_node = _view.get_drop_target(x, y);
        _remove_drag_image();
        _view.hide_drag_line();
        if (!!target_node && target_node !== _drag_target && !_is_ancestor(_drag_target, target_node)) {
            _jm.move_node(_drag_target, target_node.id);
        }
        _jm.invoke_event_handlers('dragend', { node: _drag_target, event: e });
        _drag_target = null;
        _selected_node = null;
    }

    function _is_ancestor(node, potential_ancestor) {
        var parent = node.parent;
        while (!!parent) {
            if (parent === potential_ancestor) {
                return true;
            }
            parent = parent.parent;
        }
        return false;
    }

    function _create_drag_image() {
        var node_element = _view.get_node_element(_drag_target);
        if (!node_element) {
            return;
        }
        var rect = node_element.getBoundingClientRect();
        _drag_image = $d.createElement('div');
        _drag_image.style.position = 'fixed';
        _drag_image.style.left = rect.left + 'px';
        _drag_image.style.top = rect.top + 'px';
        _drag_image.style.width = rect.width + 'px';
        _drag_image.style.height = rect.height + 'px';
        _drag_image.style.opacity = '0.7';
        _drag_image.style.zIndex = '10000';
        _drag_image.style.pointerEvents = 'none';

        var clone = node_element.cloneNode(true);
        clone.style.transform = 'none';
        clone.style.margin = '0';
        _drag_image.appendChild(clone);

        $d.body.appendChild(_drag_image);
    }

    function _update_drag_image(x, y) {
        if (!_drag_image) {
            return;
        }
        var rect = _drag_image.getBoundingClientRect();
        _drag_image.style.left = (x - rect.width / 2) + 'px';
        _drag_image.style.top = (y - rect.height / 2) + 'px';
    }

    function _remove_drag_image() {
        if (_drag_image) {
            $d.body.removeChild(_drag_image);
            _drag_image = null;
        }
    }

    // 扩展 jsmind view 方法
    var original_view = jsMind.view;
    jsMind.view = function (options) {
        var v = original_view.call(this, options);

        v.show_drag_line = function (source_node, color) {
            // 实现拖拽线显示
        };

        v.update_drag_line = function (source_node, target_node) {
            // 实现拖拽线更新
        };

        v.hide_drag_line = function () {
            // 实现拖拽线隐藏
        };

        v.get_drop_target = function (x, y) {
            var element = _view.elementFromPoint(x, y);
            return _jm.get_node(element);
        };

        return v;
    };

    jsMind.draggable = jm_draggable;

})(jsMind);