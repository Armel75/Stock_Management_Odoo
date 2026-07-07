"""
Repository SQL Server.
Couche d'accès aux données uniquement.
Ne contient AUCUNE logique métier Odoo.
Ne connaît QUE SQL Server et ses vues.

NOTE : pymssql est importé tardivement (dans les méthodes) pour éviter
de bloquer le chargement du module Odoo si le paquet n'est pas installé.
"""


# Liste canonique des vues prix par région
PRICE_VIEWS_BY_REGION = {
    'bda': 'ZPRIXBDA',
    'ber': 'ZPRIXBER',
    'cen': 'ZPRIXCEN',
    'kri': 'ZPRIXKRI',
    'ltt': 'ZPRIXLTT',
    'nga': 'ZPRIXNGA',
    'ou': 'ZPRIXOU',
}


class SqlServerRepository:
    """
    Connecteur vers les vues SQL Server de SAGE X3.
    Retourne des données brutes (listes de dictionnaires).
    """

    def __init__(self, host, port, user, password, database, schema='dbo'):
        self._host = host
        self._port = port or 1433
        self._user = user
        self._password = password
        self._database = database
        self._schema = schema

    def _connect(self):
        """
        Établit et retourne une connexion au serveur SQL Server.
        """
        import pymssql
        connection = pymssql.connect(
            server=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            timeout=0,
            login_timeout=15,
        )
        return connection

    def test_connection(self):
        """
        Teste la connexion au serveur SQL Server.

        Returns:
            tuple (success: bool, message: str)
        """
        import pymssql
        try:
            conn = self._connect()
            conn.close()
            return True, 'Connexion réussie au serveur SQL Server.'
        except pymssql.OperationalError as e:
            return False, f'Erreur de connexion : {str(e)}'
        except Exception as e:
            return False, f'Erreur inattendue : {str(e)}'

    def get_stock_data(self, view_name='ZSTOAG'):
        """
        Récupère les données de stock depuis la vue SQL Server.

        Args:
            view_name: Nom de la vue stock (défaut: ZSTOAG)

        Returns:
            list[dict] : Liste des enregistrements de stock.
        """
        full_view = f"{self._schema}.{view_name}"
        query = f"""
            SELECT
                ITMREF_0      AS default_code,
                ITMDES1_0     AS name,
                SEAKEY_0      AS search_key,
                STOFCY_0      AS site_id,
                QTE_0         AS quantity,
                CUMALLQTY_0   AS cumulative_quantity,
                STA_0         AS status
            FROM {full_view}
        """
        return self._execute_query(query)

    def get_price_data(self, view_name='ZPRIXBDA'):
        """
        Récupère les données de prix depuis UNE vue SQL Server.

        Args:
            view_name: Nom de la vue prix

        Returns:
            list[dict]
        """
        full_view = f"{self._schema}.{view_name}"
        query = f"""
            SELECT
                PLICRI2_0     AS default_code,
                SEAKEY_0      AS search_key,
                ITMDES1_0     AS name,
                TEXTE_0       AS text,
                PLICRI3_0     AS plicri3,
                PRIXHT_0      AS price_ht,
                PRIXTTC_0     AS price_ttc,
                MINQTY_0      AS min_qty,
                MAXQTY_0      AS max_qty
            FROM {full_view}
        """
        return self._execute_query(query)

    def get_all_prices_by_region(self):
        """
        Récupère les prix de TOUTES les régions en une seule fois.

        Returns:
            dict[str, list[dict]] : 
                Clé = code région (bda, ber, cen, ...)
                Valeur = liste des prix pour cette région
        """
        result = {}
        for region, view_name in PRICE_VIEWS_BY_REGION.items():
            result[region] = self.get_price_data(view_name)
        return result

    def get_full_stock_and_all_prices(self, view_stock='ZSTOAG'):
        """
        Récupère le stock + synchronise les prix par région.
        Stratégie : on récupère le stock une fois, puis les prix région par région.
        Retourne un dict structuré pour le service.

        Returns:
            dict: {
                'stock': list[dict],
                'prices_by_region': dict[str, list[dict]],
            }
        """
        stock = self.get_stock_data(view_stock)
        prices_by_region = self.get_all_prices_by_region()
        return {
            'stock': stock,
            'prices_by_region': prices_by_region,
        }

    def get_all_stock_and_prices_single_connection(self, view_stock='ZSTOAG'):
        """
        Récupère le stock ET tous les prix en une seule connexion.

        Returns:
            dict: {
                'stock': list[dict],
                'prices_by_region': dict[str, list[dict]],
            }
        """
        import pymssql

        conn = self._connect()
        try:
            # === Stock ===
            stock_view = f"{self._schema}.{view_stock}"
            stock_query = f"""
                SELECT
                    ITMREF_0      AS default_code,
                    ITMDES1_0     AS name,
                    SEAKEY_0      AS search_key,
                    STOFCY_0      AS site_id,
                    QTE_0         AS quantity,
                    CUMALLQTY_0   AS cumulative_quantity,
                    STA_0         AS status
                FROM {stock_view}
            """
            stock_data = self._execute_query_on_conn(conn, stock_query)

            # === Prix par région ===
            prices_by_region = {}
            for region, view_name in PRICE_VIEWS_BY_REGION.items():
                price_view = f"{self._schema}.{view_name}"
                price_query = f"""
                    SELECT
                        PLICRI2_0     AS default_code,
                        SEAKEY_0      AS search_key,
                        ITMDES1_0     AS name,
                        TEXTE_0       AS text,
                        PLICRI3_0     AS plicri3,
                        PRIXHT_0      AS price_ht,
                        PRIXTTC_0     AS price_ttc,
                        MINQTY_0      AS min_qty,
                        MAXQTY_0      AS max_qty
                    FROM {price_view}
                """
                prices_by_region[region] = self._execute_query_on_conn(conn, price_query)

            return {
                'stock': stock_data,
                'prices_by_region': prices_by_region,
            }
        finally:
            conn.close()

    def _execute_query_on_conn(self, conn, query):
        """
        Exécute une requête SQL sur une connexion existante.

        Args:
            conn: Connexion pymssql ouverte
            query: Requête SQL à exécuter

        Returns:
            list[dict]
        """
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            cleaned = []
            for row in rows:
                cleaned_row = {}
                for key, value in row.items():
                    if isinstance(value, str):
                        cleaned_row[key] = value.strip()
                    else:
                        cleaned_row[key] = value
                cleaned.append(cleaned_row)
            return cleaned

    def _execute_query(self, query):
        """
        Exécute une requête SQL et retourne les résultats sous forme de liste de dictionnaires.

        Args:
            query: Requête SQL à exécuter

        Returns:
            list[dict]

        Raises:
            pymssql.Error: En cas d'erreur d'exécution
        """
        import pymssql
        conn = self._connect()
        try:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                cleaned = []
                for row in rows:
                    cleaned_row = {}
                    for key, value in row.items():
                        if isinstance(value, str):
                            cleaned_row[key] = value.strip()
                        else:
                            cleaned_row[key] = value
                    cleaned.append(cleaned_row)
                return cleaned
        except pymssql.Error as e:
            raise
        finally:
            conn.close()
