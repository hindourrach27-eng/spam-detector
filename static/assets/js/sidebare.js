function sidebare(listt) {
    console.log(listt)
    if (listt.includes(2) || listt.includes(3) || listt.includes(4) || listt.includes(5)) {
        document.getElementById("nav-server_dashboard").style.display = 'block';
        document.getElementById("nav-mailer_dashboard").style.display = 'block';
        document.getElementById("nav-add_send").style.display = 'block';
        document.getElementById("nav-add_servers").style.display = 'block';
        document.getElementById("nav-add_gmail_box").style.display = 'block';
        // document.getElementById("nav-team_management").style.display = 'block';
        document.getElementById("nav-add_ip_state").style.display = 'block';
    }
    if (listt.includes(1)) {
        // document.getElementById("nav-server_dashboard").style.display = 'block';
        document.getElementById("nav-mailer_dashboard").style.display = 'block';
        document.getElementById("nav-add_send").style.display = 'block';
        // document.getElementById("nav-add_servers").style.display = 'block';
        // document.getElementById("nav-add_gmail_box").style.display = 'block';
        // document.getElementById("nav-team_management").style.display = 'block';
        // document.getElementById("nav-add_ip_state").style.display = 'block';
    }
}



