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
