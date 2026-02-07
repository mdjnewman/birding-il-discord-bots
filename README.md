eBird Rarities Bot & Birding Illinois Agree Bot
===============================================

Some Discord bots originally for the Birding Illinois server/guild.

Kudos to [@oliverburrus](https://github.com/oliverburrus/) for initially writing these.

eBird Rarities Bot (alerts for eBird notable observations)
----------------------------------------------------------

The `eBird Rarities Bot` will attempt to post only to servers configured in [servers.py](birding_il_bots/rare_bird_alerts/servers.py).

The eBird `Recent notable observations` API returns a lot of results that we don't really consider worth posting (e.g. high counts), so anything that matches the [exclude lists](./data/) is filtered out.

Text in parenthesis is trimmed from the name before matching (e.g. `(hybrid)`).

Shout out if you want to add a new server! Any `country`, `subnational1` (state), `subnational2` (county in the US) or `location` (e.g. hotspot) can be used, and exclude lists can be set per region.

Birding IL Agree Bot
--------------------

Handles users agreeing to the rules and sets their nickname. Birding IL server only.

Development
-----------

### Upgrading dependencies

```sh
cd birding_il_bots/
pip install pip-tools
pip-compile --upgrade
```

### Running locally

```sh
# Assuming you're a member and have a config with this name. To read some required secrets & RBA exclude list.
gcloud config configurations activate birding-il
python -m birding_il_bots.main
```

### Pushing a new image

No pipeline for this yet:

```sh
docker build -t us.gcr.io/birding-il/birding-il-bots:latest . && docker push us.gcr.io/birding-il/birding-il-bots:latest
```

### Deploying

```sh
gcloud compute ssh --zone "us-central1-a" --project "birding-il" --command="sudo systemctl restart cloudservice.service" birding-il-bot-compute
```
