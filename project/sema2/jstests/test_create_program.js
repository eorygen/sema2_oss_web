casper.test.comment('Test create Program');

var helper = require('./djangocasper.js');

helper.scenario('/',

    function() {

        helper.assertAbsUrl('/home/', "Directed to home after load");
        this.test.assertSelectorHasText('p[class="list-group-item-text"]', 'Download SEMA for iOS', "Home page has iOS download button");
        //this.click('input[type="button"]');
    },

    function() {

        helper.assertAbsUrl('/login/', "After clicking Login, we're redirected to login page");
    }
);

helper.run();