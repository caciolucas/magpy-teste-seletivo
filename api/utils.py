import requests


class PYPIClient:
    BASE_URL = "https://pypi.org/pypi"

    def getPackageOr404(self, package_name: str, version_specified: str = None):
        # Request to verify if package exists and version exists (if provided)
        response = requests.get(
            f'{self.BASE_URL}/{package_name}/{version_specified + "/json" if version_specified else "json"}'
        )

        if response.status_code == 200:
            # Retrieve package info
            package = response.json().get("info")
            # Set version to latest if not specified
            version = version_specified if version_specified else package["version"]
            result = {"exists": True, "package": package, "version": version}
        else:
            result = {"exists": False, "code": response.status_code}
        return result


pypiclient = PYPIClient()
