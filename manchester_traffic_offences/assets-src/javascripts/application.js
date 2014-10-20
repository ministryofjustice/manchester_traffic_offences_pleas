function showHideCheckboxToggledContent() {

    $(".block-label input[type='checkbox']").each(function () {
        var $checkbox = $(this);
        var $checkboxLabel = $(this).parent();

        var $dataTarget = $checkboxLabel.attr('data-target');

        // Add ARIA attributes

        // If the data-target attribute is defined
        if (typeof $dataTarget !== 'undefined' && $dataTarget !== false) {
            // Set aria-controls
            $checkbox.attr('aria-controls', $dataTarget);

            // Set aria-expanded and aria-hidden
            $checkbox.attr('aria-expanded', 'false');
            $('#' + $dataTarget).attr('aria-hidden', 'true');

            // For checkboxes revealing hidden content
            $checkbox.on('click', function () {
                var state = $(this).attr('aria-expanded') === 'false' ? true : false;

                // Toggle hidden content
                $('#' + $dataTarget).toggle();

                // Update aria-expanded and aria-hidden attributes
                $(this).attr('aria-expanded', state);
                $('#' + $dataTarget).attr('aria-hidden', !state);

            });
        }
    });
}

function showHideRadioToggledContent() {

    $(".block-label input[type='radio']").each(function () {
        var $radio = $(this);
        var $radioGroupName = $(this).attr('name');
        var $radioLabel = $(this).parent();

        var $dataTarget = $radioLabel.attr('data-target');

        // Add ARIA attributes

        // If the data-target attribute is defined
        if (typeof $dataTarget !== 'undefined' && $dataTarget !== false) {
            // Set aria-controls
            $radio.attr('aria-controls', $dataTarget);

            // Set aria-expanded and aria-hidden
            $radio.attr('aria-expanded', 'false');
            $('#' + $dataTarget).attr('aria-hidden', 'true');

            // For radio buttons revealing hidden content
            $radio.on('click', function () {
                var state = $(this).attr('aria-expanded') === 'false' ? true : false;

                // Toggle hidden content
                $('#' + $dataTarget).toggle();

                // Update aria-expanded and aria-hidden attributes
                $(this).attr('aria-expanded', state);
                $('#' + $dataTarget).attr('aria-hidden', !state);
            });
        }

        // If the data-target attribute is undefined for a radio button,
        // hide visible data-target content for radio buttons in the same group
        else {
            $radio.on('click', function () {
                // Select radio buttons in the same group
                $(".block-label input[name=" + $radioGroupName + "]").each(function () {
                    var groupDataTarget = $(this).parent().attr('data-target');

                    // Hide toggled content
                    $('#' + groupDataTarget).hide();

                    // Update aria-expanded and aria-hidden attributes
                    if ($(this).attr('aria-controls')) {
                        $(this).attr('aria-expanded', 'false');
                    }
                    $('#' + groupDataTarget).attr('aria-hidden', 'true');
                });
            });
        }
    });
}


function showSingleRadioContent() {
    var allTargets = {};

    // convert the aria id list, e.g. aria-controls="first_elem second_elem ..." to
    // a jQuery compatible selector, e.g. #first_elem,#second_elem ...
    var prefixHash = function(target){
        return target.split(' ').map(function(x){ return '#'+x; }).join(',');
    };

    $(".block-label input[type='radio'], .radio-label input[type='radio']").each(function () {
        var $radio = $(this);
        var $radioGroupName = $(this).attr('name');
        var $radioLabel = $(this).parent();

        var $dataTarget = $radioLabel.attr('data-target');

        var targetSel = prefixHash($dataTarget);

        if ($radioGroupName in allTargets){
            allTargets[$radioGroupName].push(targetSel);
        }
        else{
            allTargets[$radioGroupName] = [targetSel];
        }

        $radio.on('click', function () {
            $(".block-label input[name=" + $radioGroupName + "],  .radio-label input[name=" + $radioGroupName + "]").each(function () {
                // hide radio button content and reset aria values
                var groupDataTarget = $(this).parent().attr('data-target');

                var groupTargetSel = prefixHash(groupDataTarget);

                // Update aria-expanded and aria-hidden attributes
                if ($(this).attr('aria-controls')) {
                    $(this).attr('aria-expanded', 'false');
                }
                $(groupTargetSel).attr('aria-hidden', 'true');
                $(groupTargetSel).hide();
            });

            selected = $(".block-label[data-target='" + $dataTarget + "'] input[name=" + $radioGroupName + "]");

            if (selected.attr('aria-controls')) {
                selected.attr('aria-expanded', 'true');
            }

            $(targetSel).show();
            $(targetSel).attr('aria-hidden', 'false');
        });
    });

    $("input[type='radio']:checked").click();
}


function hashInputFields(){
    var all_values = "";
    $('input').each(function(){
        var $field = $(this);
        var val;
        var type = $field.attr('type');

        if ($field.is('select')) {
            type = 'select';
        }

        switch (type) {
            case 'checkbox':
            case 'radio':
                val = $field.is(':checked');
                break;
            case 'select':
                val = '';
                $field.find('option').each(function(o) {
                    var $option = $(this);
                    if ($option.is(':selected')) {
                        val += $option.val();
                    }
                });
                break;
            default:
                val = $field.val();
        }

        all_values += val;

    });

    return all_values;
}


function alertIfFieldsChanged(){
    GOVUK.form_hash = hashInputFields();
    GOVUK.form_check = true;

    $("form").on("submit", function(){
        GOVUK.form_check = false;
    });

    $(window).on("beforeunload", function () {
        if(GOVUK.form_check) {
            var form_state = hashInputFields();
            if (form_state != GOVUK.form_hash) {
                return "You have entered some information";
            }
        }
    });
}


/*
 * An aria aware toggle function
 *
 * Usage:
 *
 * onClickToggleContainer('#link', '.target,#target2...');
 */
function onClickToggleContainer(toggleSelector, targetSelectors){
    // an aria aware toggle function

    $(toggleSelector).click(function(event){

        if(!$(this).hasClass('toggled')){
            $(this).addClass('toggled');
        }
        else{
            $(this).removeClass('toggled');
        }

        $(targetSelectors).each(function(){
            $(this).toggle();

            if($(this).is(":visible")){
                if ($(this).attr('aria-controls')) {
                    $(this).attr('aria-expanded', 'true');
                }

                $(this).attr('aria-hidden', 'false');
            }
            else{
                if ($(this).attr('aria-controls')) {
                    $(this).attr('aria-expanded', 'false');
                }

                $(this).attr('aria-hidden', 'true');
            }
        });

        event.preventDefault();
    });
}


$(document).ready(function () {
    jQuery.fx.off = true;

    var $blockLabels = $(".block-label input[type='radio'], .block-label input[type='checkbox']");
    GOVUK.selectionButtons($blockLabels);

    showSingleRadioContent();

    onClickToggleContainer('#case_contact_link a', '#case_contact_details');

    alertIfFieldsChanged();
});