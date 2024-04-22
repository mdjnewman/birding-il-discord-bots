Birding Illinois Discord server bots
====================================

Some Discord bots for the Birding Illinois server/guild.

Kudos to [@oliverburrus](https://github.com/oliverburrus/) for initially writing these.

Pushing a new image
-------------------

No pipeline for this yet:

```sh
docker build -t us.gcr.io/birding-il/birding-il-bots:latest .
docker push us.gcr.io/birding-il/birding-il-bots:latest
```

Deploying
---------

```sh
gcloud compute ssh \
    --plain \
    --zone "us-central1-a" \
    --project "birding-il" \
    --command="sudo systemctl restart cloudservice.service" \
    birding-il-bot-compute
```
