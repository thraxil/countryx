var gCurrentChoice = 0;

function debug(string) {
    log(string);
}

function clearChoice(control) {
    clearMessages();
    gCurrentChoice = 0;

    jQuery('.player_choice')
        .show()
        .parent()
        .removeClass('active');
    jQuery('#reasoning_form').toggle(500);
}

function choose(control, choice) {
    if (gCurrentChoice === 0 ||
        gCurrentChoice === undefined ||
        gCurrentChoice === '') {
        gCurrentChoice = choice;

        jQuery('.player_choice')
            .hide()
            .parent()
            .removeClass('active');
        jQuery('#' + choice)
            .show()
            .parent()
            .toggleClass('active');
        jQuery('#reasoning_form').toggle(500, 'linear');
    }
}

function clearMessages() {
    setStyle($('successMsg'), {'display': 'none'});
    setStyle($('errorMsg'), {'display': 'none'});
    setStyle($('errorClient'), {'display': 'none'});
}

function saveChoiceSuccess(response) {
    var doc = JSON.parse(response.responseText, null);

    if (doc.result === 0) {
        $('errorMsg').innerHTML = 'An error occurred while saving your ' +
            'choices. Please logout and log back in again and try to resubmit.';
        setStyle($('errorMsg'), {'display': 'block'});
    } else if (doc.result == 1) {
        // draft -- leave the screen the way it was
        $('successMsg').innerHTML = 'Your choices have been saved.';
        setStyle($('successMsg'), {'display': 'block'});

        // enable the buttons
        $('savedraft').disabled = false;
        $('submit').disabled = false;
        $('clear').disabled = false;
    } else if (doc.result == 2) {
        // submit succeeded -- hide the selection divs

        // submit -- leave the screen the way it was
        $('successMsg').innerHTML = 'Your choices have been submitted.';
        setStyle($('successMsg'), {'display': 'block'});

        $(gCurrentChoice).onclick = '';
        setNodeAttribute($('reasoning'), 'readonly', 'true');
        setStyle($('savedraft'), {'display': 'none'});
        setStyle($('submit'), {'display': 'none'});
        setStyle($('clear'), {'display': 'none'});
        $('submit_state_desc').innerHTML = 'Final Submission';
    }
}

function saveChoiceError(err) {
    $('errorMsg').innerHTML = err + '. This is probably a temporary error. ' +
        'We recommend that you log out and log back in again and try to ' +
        'resubmit.';
    setStyle($('errorMsg'), {'display': 'block'});
}

function saveChoice(control, finalsubmit) {
    clearMessages();

    if (finalsubmit && $('reasoning').value.length < 1) {
        $('errorClient').innerHTML = 'Please enter your reasoning ' +
            'before submitting a final answer.';
        setStyle($('errorClient'), {'display': 'block'});
    } else if (finalsubmit && !confirm(
        'Are you sure you\'re ready to ' +
            'submit your choice and reasoning? ' +
            'Your responses are final once you ' +
            'hit OK')) {
        return; // do nothing
    } else if (gCurrentChoice === 0) {
        alert('DEBUG: Current Choice is 0');
    } else {
        // disable the buttons
        $('savedraft').disabled = true;
        $('submit').disabled = true;
        $('clear').disabled = true;

        var parts = location.href.split('/');
        var groupid = parts[parts.length - 2];
        var url = location.protocol + '//' + location.hostname + ':' +
            location.port + '/sim/player/choose/';

        var q = queryString(
            {
                'groupid': groupid, 'choiceid': gCurrentChoice,
                'final': finalsubmit, 'reasoning': $('reasoning').value
            });
        var deferred = doXHR(
            url,
            {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                sendContent: q
            }
        );
        deferred.addCallbacks(saveChoiceSuccess, saveChoiceError);
    }
}

function initializeGame() {
    gCurrentChoice = $('current_choice').innerHTML;
}
MochiKit.Signal.connect(window, 'onload', initializeGame);
