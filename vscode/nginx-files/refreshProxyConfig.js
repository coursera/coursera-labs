const NginxConfFile = require('nginx-conf').NginxConfFile;
const easyConfig = require('/home/nginx/reverseProxyConfig.json')

const filename = `/home/nginx/reverse-proxy.conf`

NginxConfFile.create(filename, function (err, conf) {
    if (err || !conf) {
        console.log(err);
        return;
    }

    const onFlushed = () => {
        console.log('finished writing to disk');
    };

    conf.on('flushed', onFlushed);

    // write to a different file
    conf.live(`${filename}.bak`);

    // force the synchronization
    conf.flush();

    let validationError = false;

    // validate reverse-proxy inputs
    // entrypoint and launchPath must be strings
    // port must be a number
    easyConfig['reverse-proxy'].forEach((opts) => {
        if  (typeof opts.entrypoint !== 'string') {
            console.log("Make sure all of your `entrypoint` values are strings");
            validationError = true;
        }
        if (typeof opts.port !== 'number') {
            console.log("Make sure all of your `port` values are numbers")
            validationError = true;
        }
        if (!!opts.launchPath && typeof opts.launchPath !== 'string') {
            console.log("Make sure all of your `launchPath` values are strings");
            validationError = true;
        }
    })

    // Go no further if a validation error is detected
    if (validationError) {
        console.log("Please fix your reverseProxyConfig.json file and try again");
        conf.off('flushed', onFlushed);
        return;
    }

    // delete all existing location directives
    let locationLength = (conf.nginx.server[0].location !== undefined) ? conf.nginx.server[0].location.length : 0

    for (let i = 0; i < locationLength; i++) {
        conf.nginx.server[0]._remove('location')
    }
    
    easyConfig['reverse-proxy'].forEach((opts) => {
        // standardize strings to being and end with a single '/'
        const entrypoint = opts.entrypoint.replace(/^\/*/, '/').replace(/\/*$/, '/')
        const port = opts.port
        const launchPath = (opts.launchPath !== undefined) ? opts.launchPath.replace(/^\/*/, '/').replace(/\/*$/, '/') : "/"

        locationLength = (conf.nginx.server[0].location !== undefined) ? conf.nginx.server[0].location.length : 0
        conf.nginx.server[0]._add('location', entrypoint)
        conf.nginx.server[0].location[locationLength]._add('proxy_pass', `http://localhost:${port}${launchPath}`)

        conf.nginx.server[0]._add('location', `${launchPath}static/js/`)
        conf.nginx.server[0].location[locationLength + 1]._add('proxy_pass', `http://localhost:${port}`)
        conf.nginx.server[0].location[locationLength + 1]._add('proxy_http_version', 1.1)
        conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header Upgrade', "\'$http_upgrade\'")
        conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header Connection', "\'upgrade\'")
        conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header Host', "\'$host\'")
        conf.nginx.server[0].location[locationLength + 1]._add('proxy_cache_bypass', "\'$http_upgrade\'")

        conf.nginx.server[0]._add('location', `${launchPath}sockjs-node/`)
        conf.nginx.server[0].location[locationLength + 2]._add('proxy_pass', `http://localhost:${port}`)
        conf.nginx.server[0].location[locationLength + 2]._add('proxy_http_version', 1.1)
        conf.nginx.server[0].location[locationLength + 2]._add('proxy_set_header Upgrade', "\'$http_upgrade\'")
        conf.nginx.server[0].location[locationLength + 2]._add('proxy_set_header Connection', "\'upgrade\'")
        conf.nginx.server[0].location[locationLength + 2]._add('proxy_set_header Host', "\'$host\'")
        conf.nginx.server[0].location[locationLength + 2]._add('proxy_cache_bypass', "\'$http_upgrade\'")
    })

    locationLength = conf.nginx.server[0].location.length
    conf.nginx.server[0]._add('location', "/")
    conf.nginx.server[0].location[locationLength]._add('proxy_pass', `http://localhost:7000`)
    conf.nginx.server[0].location[locationLength]._add('proxy_set_header Host', "\'$host\'")
    conf.nginx.server[0].location[locationLength]._add('proxy_set_header X-Real-IP', "\'$remote_addr\'")
    conf.nginx.server[0].location[locationLength]._add('proxy_set_header X-Forwarded-Proto', "https")
    conf.nginx.server[0].location[locationLength]._add('proxy_set_header X-Forwarded-For', "\'$remote_addr\'")
    conf.nginx.server[0].location[locationLength]._add('proxy_set_header X-Forwarded-Host', "\'$remote_addr\'")
    conf.nginx.server[0].location[locationLength]._add('proxy_http_version', 1.1)
    conf.nginx.server[0].location[locationLength]._add('proxy_set_header Upgrade', "\'$http_upgrade\'")
    conf.nginx.server[0].location[locationLength]._add('proxy_set_header Connection', "\'upgrade\'")

    conf.nginx.server[0]._add('location', `= /static/`)
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_pass', `http://localhost:7000`)
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header Host', "\'$host\'")
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header X-Real-IP', "\'$remote_addr\'")
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header X-Forwarded-Proto', "https")
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header X-Forwarded-For', "\'$remote_addr\'")
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header X-Forwarded-Host', "\'$remote_addr\'")
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_http_version', 1.1)
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header Upgrade', "\'$http_upgrade\'")
    conf.nginx.server[0].location[locationLength + 1]._add('proxy_set_header Connection', "\'upgrade\'")

    // remove old listener
    conf.off('flushed', onFlushed);

    // kill process when done writing to disk
    conf.on('flushed', () => {
        console.log('finished writing to disk, exiting');
        process.exit();
    });

    conf.flush();
})
