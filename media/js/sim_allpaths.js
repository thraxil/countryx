/*wrap code with module pattern*/
(function() {
    var global = this;

    function onMyLoad() {
	var MyRoleSelector = new RoleSelector();
	forEach(getElementsByTagAndClassName(null,'transition-to'), function(elt) {
	    connect(elt,'onclick',zoomTransitionTo);
	});
	forEach(getElementsByTagAndClassName(null,'transition-permutation'), function(elt) {
	    connect(elt,'onmouseover',MyRoleSelector,'selectNums');
	});
    }
    connect(window,'onload',onMyLoad);

    function zoomTransitionTo(evt) {
	var elt = getFirstElementByTagAndClassName(null,'transitions',evt.src());
	var my_copy = elt.cloneNode(true);
	replaceChildNodes('fillmeup',my_copy);
	forEach(getElementsByTagAndClassName('div',null,my_copy), function(elt) {
	    elt.id = 'trans-'+elt.getAttribute('data-index');
	});
	var selector = new GridSelector(my_copy,9);
    }

    function RoleSelector() {
	//assumes 4 -- never uses index 0
	this.choices = [0,0,0,0,0];
    }

    RoleSelector.prototype.selectNums = function (evt) {
	var num = (typeof(evt.src)=='function')?Number(evt.src().getAttribute('data-index')):evt;
	var class_vals = '';

	var i = this.choices.length;
	while (--i >0) {
	    ///e.g. president[i=1] = parseInt(num%81.1/27.01) +1;
	    var ord = Math.pow(3,4-i)+0.01; //3's column
	    var parent_ord = Math.pow(3,5-i)+0.01; 
	    var choice = parseInt(num%parent_ord/ord) +1 ;
	    class_vals += ' s'+i+'-'+choice
	}
	$('gridkey').className = class_vals;
	//$('key-label').innerHTML = class_vals;
    }

    function GridSelector(grid_parent,width) {
	this.parent = grid_parent;
	this.width = width;
	this.current_selected = [];
	this.selecting = false;
	this.role_selector = new RoleSelector();

	this.__init__();
    }
    GridSelector.prototype.__init__ = function() {
	var self = this;
	forEach(self.parent.childNodes,function(elt) {
	    connect(elt,'onmousedown',self,'onMouseDown');
	    connect(elt,'onmouseup',self,'onMouseUp');
	    connect(elt,'onmouseover',self,'onMouseOver');
	});
	forEach(getElementsByTagAndClassName(null,'transition-permutation',self.parent), function(elt) {
	    connect(elt,'onmouseover',self.role_selector,'selectNums');
	});
    }

    //assumes 9x9 box
    GridSelector.prototype.selectBox = function(i,j) { 
	var mod_j =(j%9==0)?9:j%9; //last column stays 9
	var mod_i =(i%9==0)?9:i%9; //last column stays 9
	var dx = (mod_j)-(mod_i);
	var sign_x = (dx==0)?1:dx/Math.abs(dx);

	///divide by a smidgin over 9, so when j%9==0 it stays on the same line as i
	var dy = parseInt(j/9.05)-parseInt(i/9.05);
	var sign_y = (dy==0)?1:dy/Math.abs(dy);

	var a_stop = (i*1)+9*(dy+sign_y);
	for (a=(i*1); a!=a_stop && a<=81 && a>0; a=a+(9*sign_y)) {
	    var b_stop = a+dx+sign_x;
	    for (b=a; b!=b_stop && b<=81 && b>0; b=b+sign_x) {
		addElementClass('trans-'+(b*1),'selected');
	    }
	}
    }

    GridSelector.prototype.onMouseDown = function(evt) {
	var self = this;
	var my_elt = evt.src();
	var index = my_elt.getAttribute('data-index');
	self.current_selected = [index];
	self.selecting = true;
	self.updateSelected(index,true);
    }
    GridSelector.prototype.onMouseUp = function(evt) {
	var self = this;
	self.selecting = false;
    }
    GridSelector.prototype.onMouseOver = function(evt) {
	var self = this;
	if (!self.selecting) {
	    return;
	}
	var my_elt = evt.src();
	var index = my_elt.getAttribute('data-index');
	self.updateSelected(index);
    }
    GridSelector.prototype.updateSelected = function(index,purge_others) {
	var self = this;
	var s = self.current_selected;
	if (s[1] == index) {return;}
	if (purge_others
	    || (Math.abs(s[1]-s[0]) > Math.abs(index-s[0]))) {
	    
	    forEach(getElementsByTagAndClassName(null,'selected',self.parent), function(elt) {
		removeElementClass(elt,'selected');
	    });
	}
	s[1] = index;
	self.selectBox(s[0],s[1]);
    }


    


})();
