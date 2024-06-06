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
gcloud compute ssh --plain --zone "us-central1-a" --project "birding-il" --command="sudo systemctl restart cloudservice.service" birding-il-bot-compute
```

Rare Bird Alerts bot
--------------------

The `Birding IL eBird Rarities Bot` will attempt to post to a channel named `#ebird-alerts` in any guild/server it is added to.

The eBird `Recent notable observations` API returns a lot of results that we don't really consider worth posting (e.g. high counts), so anything that matches the [exclude list](./data/rare-bird-excludes.txt) is filtered out.

Text in parenthesis is trimmed from the name before matching (e.g. `(hybrid)`)
