$(function() {
    var bar_progress = [];
    var num_bars = 0;
    
    // Main function, to eventually run python script
    var concat_hash = function() {
        var hash = $("input[name='album_hash']").val();
        var dir = $("input[name='dl_dir']").val();
        var new_dir = "False";
        var empty_dir = "False";
        var quit = false;

        // Functionality for new directory checkbox/input
        if ($("#dl_new input").is(":checked")) {
            if (!$.trim($("#new_dir input").val()).length) {
                alert("With the new directory checkbox checked, you need to put in a directory to download to!");
                return false
            }
            dir += "\\" + $("#new_dir input").val();
            new_dir = "True";
        } else if ($("#dl_empty input").is(":checked")) {
            empty_dir = "True";
        }

        // Make checks on directory
        $.ajax({
            url: $SCRIPT_ROOT + "/check/",
            async: false,
            data: {
                img_dir: dir,
                new_dir: new_dir,
                empty_dir: empty_dir
            },
            success: function(data) {
                if (data.response === "dne_dir") {
                    quit = true;
                    alert("Directory does not exist, please select one that does or select option to create a new directory.");
                } else if (data.response === "nonempty_dir") {
                    quit = true;
                    alert("This directory isn't empty, if that's ok then uncheck the first option.");
                } else if (data.response === "dne_ini") {
                    quit = true;
                    alert("Could not find the .ini file, use the relative path from the position of downloader.py");
                } else if (data.response === "new_dir_exists") {
                    quit = true;
                    alert("This new directory already exists.");
                }
            },
        });
        console.log("HERE IS QUIT: " + quit);
        if (quit) {
            console.log("WE QUITTING!");
            return;
        }

        // Add progress bar
        // Album hash name
        var div_hash = $("<div>", {
            class: "prog_hash",
            text: hash
        })
        // Percentage text
        var div_per = $("<div>", {
            id: "dl_per_" + num_bars,
            class: "prog_per",
            text: "0%"
        });
        // Fill of progress bar
        var div_in = $("<div>", {
            id: "dl_in_" + num_bars,
            class: "prog_fill"
        })
        // Background of progress bar
        var div_out = $("<div>", {class: "prog_border"})
        .append(div_per).append(div_in);
        // Fraction done
        var div_frac = $("<div>", {
            id: "dl_frac_" + num_bars,
            class: "prog_frac"
        })
        var hr = $("<hr>", {class: "prog_hr"})
        // Everything together
        var div_tot = $("<div>", {class: "prog_tot"})
        .append(div_hash)
        .append(div_out)
        .append(div_frac)
        .append(hr)
        .prependTo($("#dl_list"));

        var query = "?album_hash=" + hash +
                    "&img_dir=" + dir +
                    "&new_dir=" + new_dir + 
                    "&empty_dir=" + empty_dir;
        var source = new EventSource("/download_album/" + num_bars + query);
        source.onmessage = function(e) {
            var data = JSON.parse(e.data);
            var percent = data.count/data.total*100;
            $("#dl_in_" + data.id).width(percent + "%");
            $("#dl_per_" + data.id).text(percent.toFixed(2) + "%");
            $("#dl_frac_" + data.id).text(data.count + "/" + data.total);
        };
        // Stops stream when download is done
        source.addEventListener("finished", function(e) {
            console.log("Album " + hash + " has finished downloading.");
            source.close();
        });

        // Moves on to next stream
        num_bars++;

        // Return to input box
        $("input[name='album_hash']").focus();

        return false;
    };

    // Click button or press enter
    $("#dl_btn").click(concat_hash);
    $("input[name='album_hash']").keypress(function(e) {
        if (e.keyCode == 13) {
            concat_hash();
        }
    });

    // Bring up text box for directory
    $("#dl_new").click(function() {
        $("#new_dir").toggle(this.checked);
    });
});