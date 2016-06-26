// Work around for fixing the collapsible menu not closing after selecting the list item ( courtesy:Stack Over Flow)
/* $(document).on('click', function(event){
      var $clickedOn = $(event.target),
          $collapsableItems = $('.collapse'),
          isToggleButton = ($clickedOn.closest('.navbar-toggle').length == 1),
          isLink = ($clickedOn.closest('a').length == 1),
          isOutsideNavbar = ($clickedOn.parents('.navbar').length === 0);

      if( (!isToggleButton && isLink) || isOutsideNavbar ) {
        $collapsableItems.each(function(){
          $(this).collapse('hide');
        });
      }
    });*/

$().ready(function() {
    $("#registrationForm").validate({

        rules: {
            firstName: {
                required: true,
                lettersonly: true
            },
            lastName: {
                required: true,
                lettersonly: true
            },
            userId: {
                required: true,
                minlength: 6,
                maxlength: 15,
                alphanumeric: true
            },

            password: {
                required: true,
                minlength: 6,
                maxlength: 15,
                alphanumeric: true,
                notEqualTo: "#userId"
            },

            confirmPassword: {
                required: true,
                minlength: 6,
                maxlength: 15,
                alphanumeric: true,
                equalTo: "#password"
            },

            email: {
                required: false,
                email: true,
                maxlength: 50
            }

        },

        messages: {
            firstName: {
                required: "Please enter the First name.",
                lettersonly: "Letters only please."
            },
            lastName: {
                required: "Please enter the Last name.",
                lettersonly: "Letters only please."
            },
            userId: {
                required: "Please enter the User Id.",
                minlength: "User Id must atleast by 6 characters.",
                maxlength: "User Id must be not more than 15 characters."
            },
            password: {
                required: "Please provide the password.",
                minlength: "Password must atleast by 6 characters.",
                notEqualTo: "Password cannot be same as Username.",
                maxlength: "Password must be not more than 15 characters."
            },
            confirmPassword: {
                required: "Please provide the password.",
                minlength: "Password must atleast by 6 characters.",
                equalTo: "Please enter the same password as above.",
                maxlength: "Password must be not more than 15 characters."
            },
            email: {
                email: "Please enter a valid e-mail id.",
                maxlength: "Email id must be not more than 50 characters."

            }

        }

    });

    $("#loginForm").validate({

        rules: {
            inputUserId: {
                required: true
            },

            inputPassword: {
                required: true
            }
        },
        messages: {
            inputUserId: {
                required: "Please enter the User Id."
            },
            inputPassword: {
                required: "Please provide the password."
            }

        }

    });

    $("#createEditPostForm").validate({
        rules: {
            title: {
                required: true,
                maxlength: 50
            },

            content: {
                required: true
            }
        },
        messages: {
            title: {
                required: "Please enter the title of the post.",
                maxlength: "Please keep the title less than 50 characters"
            },
            content: {
                required: "Please provide the content for this post."
            }

        }

    });

    $("#postCommentForm").validate({

        rules: {
            comment: {
                required: true,
                cannotbeempty : true
            }
        },
        messages: {
            comment: {
                required: "Comments cannot be empty.Please provide the comments."
            }
        }

    })

    $('.editComment').click(function(){
        var elementId = this.id;
        var currComment = $('#'+elementId+'Comment').text();
        $('#comment').text(currComment);
        $('#postCommentModalTitle').text("Update Comment");
        $('#postCommentButtonName').text("Update");
        $('#commentId').val(elementId);
    });

    $('.deleteComment').click(function(){
        var elementId = this.id;
        $('#commentId').val(elementId);
    });

    if($('.viewpostDiv').length > 0){
        $( window ).load(function() {
        if (window.location.href.indexOf('reload')==-1) {
             window.location.replace(window.location.href+'?reload');
        }
    });
    }


    $("#likeBtn").click(function(event){
        var isPostAuthor = $('#isPostAuthor').val();
        var hasLikedPostAlready =  $('#hasLikedPostAlready').val();
        if(isPostAuthor === "True"){
            $("#likeErrors").fadeIn(1000);
            $("#likeErrors").text("You cannot 'LIKE' your own posts.");
            $("#likeErrors").css("display","block");
            $("#likeErrors").fadeOut(2000);
            event.preventDefault();
        }

        if(hasLikedPostAlready !== "0"){
            $("#likeErrors").fadeIn(1000);
            $("#likeErrors").text("You have 'LIKED' this post already.");
            $("#likeErrors").css("display","block");
            $("#likeErrors").fadeOut(2000);
            event.preventDefault();
        }

        
    });
});

//Custom Validations as per Blog0440 application
$.validator.addMethod("alphanumeric", function(value, element) {
    return this.optional(element) || (/^\w+$/i.test(value));
}, "Letters, numbers, and underscores only please");

$.validator.addMethod("lettersonly", function(value, element) {
    return this.optional(element) || (/^[a-z]+$/i.test(value));
}, "Letters only please");

$.validator.addMethod("cannotbeempty", function(value, element) {
    if(value.trim() === ""){
        return false;
    }else{
        return true;
    }
}, "Comments cannot be empty.Please provide the comments.");