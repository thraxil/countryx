/*wrap code with module pattern*/
(function() {
    var global = this;

    function onMyLoad() {
	forEach(getElementsByTagAndClassName(null,'transition-to'), function(elt) {
	    connect(elt,'onclick',zoomTransitionTo);
	});
    }
    connect(window,'onload',onMyLoad);

    function zoomTransitionTo(evt) {
	var elt = getFirstElementByTagAndClassName(null,'transitions',evt.src());
	var my_copy = elt.cloneNode(true);
	replaceChildNodes('fillmeup',my_copy);
	var selector = new GridSelector(my_copy,9);
    }

    function GridSelector(grid_parent,width) {
	this.parent = grid_parent;
	this.width = width;
	this.current_selected = [];
	this.selecting = false;
	this.__init__();
    }
    GridSelector.prototype.__init__ = function() {
	var self = this;
	forEach(self.parent.childNodes,function(elt) {
	    connect(elt,'onmousedown',self,'onMouseDown');
	    connect(elt,'onmouseup',self,'onMouseUp');
	    connect(elt,'onmouseover',self,'onMouseOver');
	});

    }    
    GridSelector.prototype.onMouseDown = function(evt) {
	var self = this;
	var my_elt = evt.src();
	self.current_selected = [my_elt];
	self.selecting = true;
	self.updateSelected(true);
    }
    GridSelector.prototype.onMouseUp = function(evt) {
	var self = this;
	self.selecting = false;
	var my_elt = evt.src();
	self.current_selected.push(my_elt);
	self.updateSelected();
    }
    GridSelector.prototype.onMouseOver = function(evt) {
	var self = this;
	if (!self.selecting) {
	    return;
	}
	var my_elt = evt.src();
	self.current_selected.push(my_elt);
	self.updateSelected();
    }
    GridSelector.prototype.updateSelected = function(purge_others) {
	var self = this;
	if (purge_others) {
	    
	    forEach(getElementsByTagAndClassName(null,'selected',self.parent), function(elt) {
		removeElementClass(elt,'selected');
	    });
	}
	forEach(self.current_selected, function(elt) {
	    addElementClass(elt,'selected');
	});
    }
})();
