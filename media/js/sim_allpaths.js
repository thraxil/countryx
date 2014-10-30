/*wrap code with module pattern*/
(
    function() {
        var global = this;

        function onMyLoad() {
            var MyRoleSelector = new RoleSelector();
            forEach(
                getElementsByTagAndClassName(null, 'transition-to'),
                function(elt) {
                    connect(elt, 'onclick', zoomTransitionTo);
                });
            forEach(
                getElementsByTagAndClassName(null, 'transition-permutation'),
                function(elt) {
                    connect(elt, 'onmouseover', MyRoleSelector, 'selectNums');
                });
        }
        connect(window, 'onload', onMyLoad);

        function zoomTransitionTo(evt) {
            var elt = getFirstElementByTagAndClassName(
                null, 'transitions', evt.src());
            var myCopy = elt.cloneNode(true);
            replaceChildNodes('fillmeup', myCopy);
            forEach(getElementsByTagAndClassName('div', null, myCopy),
                    function(elt) {
                        elt.id = 'trans-' + elt.getAttribute('data-index');
                    });
            var selector = new GridSelector(myCopy, 9);
        }

        function RoleSelector() {
            //assumes 4 -- never uses index 0
            this.choices = [0, 0, 0, 0, 0];
        }

        RoleSelector.prototype.selectNums = function(evt) {
            var num = (typeof(evt.src) == 'function') ?
                Number(evt.src().getAttribute('data-index')) : evt;
            var classVals = '';

            var i = this.choices.length;
            while (--i > 0) {
                var ord = Math.pow(3, 4 - i) + 0.01; //3's column
                var parentOrd = Math.pow(3, 5 - i) + 0.01;
                var choice = parseInt(num % parentOrd / ord) + 1;
                classVals += ' s' + i + '-' + choice;
            }
            if ($('gridkey')) {
                $('gridkey').className = classVals;
            }
        };

        function GridSelector(gridParent, width) {
            this.parent = gridParent;
            this.width = width;
            this.currentSelected = [];
            this.selecting = false;
            this.roleSelector = new RoleSelector();
            this.__init__();
        }
        GridSelector.prototype.__init__ = function() {
            var self = this;
            forEach(self.parent.childNodes, function(elt) {
                connect(elt, 'onmousedown', self, 'onMouseDown');
                connect(elt, 'onmouseup', self, 'onMouseUp');
                connect(elt, 'onmouseover', self, 'onMouseOver');
            });
            forEach(
                getElementsByTagAndClassName(
                    null, 'transition-permutation', self.parent),
                function(elt) {
                    connect(elt, 'onmouseover', self.roleSelector,
                            'selectNums');
                });
        };

        //assumes 9x9 box
        GridSelector.prototype.selectBox = function(i, j) {
            var modJ = (j % 9 === 0) ? 9 : j % 9; //last column stays 9
            var modI = (i % 9 === 0) ? 9 : i % 9; //last column stays 9
            var dx = modJ - modI;
            var signX = (dx === 0) ? 1 : dx / Math.abs(dx);

            ///divide by a smidgin over 9, so when j%9==0 it stays on the same line as i
            var dy = parseInt(j / 9.05) - parseInt(i / 9.05);
            var signY = (dy === 0) ? 1 : dy / Math.abs(dy);

            var aStop = (i * 1) + 9 * (dy + signY);
            for (var a = (i * 1);
                 a != aStop && a <= 81 && a > 0;
                 a = a + (9 * signY)) {
                var bStop = a + dx + signX;
                for (var b = a; b != bStop && b <= 81 && b > 0; b = b + signX) {
                    addElementClass('trans-' + (b * 1), 'selected');
                }
            }
        };

        GridSelector.prototype.onMouseDown = function(evt) {
            var self = this;
            var myElt = evt.src();
            var index = myElt.getAttribute('data-index');
            self.currentSelected = [index];
            self.selecting = true;
            self.updateSelected(index, true);
        };
        GridSelector.prototype.onMouseUp = function(evt) {
            var self = this;
            self.selecting = false;
        };
        GridSelector.prototype.onMouseOver = function(evt) {
            var self = this;
            if (!self.selecting) {
                return;
            }
            var myElt = evt.src();
            var index = myElt.getAttribute('data-index');
            self.updateSelected(index);
        };
        GridSelector.prototype.updateSelected = function(index, purgeOthers) {
            var self = this;
            var s = self.currentSelected;
            if (s[1] == index) {
                return;
            }
            if (purgeOthers ||
                (Math.abs(s[1] - s[0]) > Math.abs(index - s[0]))) {

                forEach(
                    getElementsByTagAndClassName(null, 'selected', self.parent),
                    function(elt) {
                        removeElementClass(elt, 'selected');
                    });
            }
            s[1] = index;
            self.selectBox(s[0], s[1]);
        };
    })();
