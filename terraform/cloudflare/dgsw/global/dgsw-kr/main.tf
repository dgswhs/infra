import {
  to = cloudflare_zone.dgsw_kr
  id = "cb0c3f734e75ef8396ab0861be2d4909"
}

import {
  to = cloudflare_dns_record.spot
  id = "cb0c3f734e75ef8396ab0861be2d4909/287a16b454b64d50aecedf5af2ea4b6c"
}

resource "cloudflare_zone" "dgsw_kr" {
  account = {
    id = local.account_id
  }
  name = "dgsw.kr"
  type = "full"
}

resource "cloudflare_dns_record" "spot" {
  zone_id = cloudflare_zone.dgsw_kr.id
  name    = "spot.dgsw.kr"
  type    = "CNAME"
  content = "8c5a8e7a208d415d.vercel-dns-017.com"
  proxied = false
  ttl     = 1
}
