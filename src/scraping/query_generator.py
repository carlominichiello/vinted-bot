from urllib.parse import urlparse, parse_qs


class QueryGenerator:

    def get_query(self, vinted_url):
        parsed_url = urlparse(vinted_url)
        if parsed_url.netloc != "www.vinted.fr":
            raise ValueError(f"Invalid url: {vinted_url}")

        query = parse_qs(parsed_url.query)
        query.pop('search_id', None)

        params = {**query}
        for key, value in query.items():
            if key.endswith('[]'):
                params[key[:-2]] = value
                params.pop(key)

        if 'catalog' in params:
            params['catalog_ids'] = params.pop('catalog')

        return params
