/**

Copyright (C) 2008 GestorPsi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

*/

$(function(){


    // show and hide search by matrix year
    $('input#filter_student_matrix_year').click(function(){
        if (this.checked){
            $("div#div_student_matrix_year_input").show();
        }else{
            $("div#div_student_matrix_year_input").hide();
            $("input[name=search_student_matrix_year]").val('');
        }
    });

    /**
     * student initial filter deactive
     */
    $('div#search_header.student_search.deactive table#letter_menu tr td a, div#search_header.student_search.deactive a#letter_back, div#search_header.student_search.deactive a#letter_fwd').click(function(){
        matrix_year = $("input[name=search_student_matrix_year]").val();
        updateStudent('/careprofessional/student/initial/' + $(this).attr('initial') + '/page1/deactive/?matrixyear=' + matrix_year, true, 'careprofessional/student/initial/' + $(this).attr('initial'), '?matrixyear=' + matrix_year);
    });

    /**
    * student quick search deactive
    */
    $('div#search_header.student_search.deactive a.quick_search').click(function() {
        matrix_year = $("input[name=search_student_matrix_year]").val();
        ($(this).prev().val().length >= 1) ? updateStudent('/careprofessional/student/filter/' + $(this).prev().val() + '/page1/deactive/?matrixyear=' + matrix_year, true, 'careprofessional/student/filter/' + $(this).prev().val(), '?matrixyear=' + matrix_year) : updateStudent('/careprofessional/student/page1/deactive/?matrixyear=' + matrix_year, true, '?matrixyear' + matrix_year);
    });
    
    /**
     * student clean up deactive
     */
    $('div#search_header.student_search.deactive a#cleanup').click(function() {
        updateStudent('/careprofessional/student/page1/deactive/', true);
    });

    /**
     * student initial filter active
     */
    $('div#search_header.student_search.active table#letter_menu tr td a, div#search_header.student_search.active a#letter_back, div#search_header.student_search.active a#letter_fwd').click(function() {
        matrix_year = $("input[name=search_student_matrix_year]").val();
        updateStudent('/careprofessional/student/initial/' + $(this).attr('initial') + '/page1/?matrixyear=' + matrix_year, false, 'careprofessional/student/initial/'+$(this).attr('initial'));
    });

    /**
    * student quick search active
    */
    $('div#search_header.student_search.active a.quick_search').click(function() {
        matrix_year = $("input[name=search_student_matrix_year]").val();
        ($(this).prev().val().length >= 1) ? updateStudent('/careprofessional/student/filter/' + $(this).prev().val() + '/page1/?matrixyear=' + matrix_year, false, 'careprofessional/student/filter/'+$(this).prev().val(), '?matrixyear=' + matrix_year) : updateStudent('/careprofessional/student/page1/?matrixyear=' + matrix_year);
    });

    /**
     * student clean up active
     */
    $('div#search_header.student_search.active a#cleanup').click(function() {
        updateStudent('/careprofessional/student/page1');
    });

});
