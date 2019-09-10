from django.conf import settings
from txlib_too import registry
from txlib_too.http import auth
from txlib_too.http.exceptions import NotFoundError, RemoteServerError
from txlib_too.http import http_requests
from txlib_too.api import (
    project,
    resources,
    translations,
    statistics,
)

LOCALES = ('fr_CA', 'fr_FR', 'es_ES')

UNTRANSLATED_LOCALES = ('en', 'en-us',)
DEFAULT_SOURCE_LANGUAGE = 'en_US'
DEFAULT_I18N_TYPE = 'HTML'


class Tx(object):

    def __init__(self, project_slug_prefix):

        self.__project_slug_prefix = project_slug_prefix

        self.setup_registry()

    def projects(self):
        """Yield (project, lang) tuples for all help center projects."""

        project.Project._http.get(
            project.Project._construct_path_to_collection()
        )

    def get_project(self, locale, source_language_code=DEFAULT_SOURCE_LANGUAGE, **kwargs):
        """
        Gets or creates the Transifex project for the current project prefix and locale

        :param locale: A locale to which content is to be translated
        :type locale: string
        :param source_language_code: The language of the original untranslated content (i.e. Spanish),
            defaults to DEFAULT_SOURCE_LANGUAGE, which is English
        :type source_language_code: string, optional
        :return: The Transifex project to which resources can be pushed or pulled
        :rtype: project.Project
        """

        try:
            locale_project = project.Project.get(slug=self.get_project_slug(locale))

        except NotFoundError:

            locale_project = project.Project(
                slug=self.get_project_slug(locale),
            )
            defaults = {
                'name': 'Help Center (%s)' % (locale, ),
                'description': 'Help Center pages to translate to %s' % (
                    locale,
                ),
                'source_language_code': source_language_code,
                'private': True,
            }

            valid_keys = ('name', 'description')
            defaults.update(
                {k: v for k, v in kwargs.items() if k in valid_keys}
            )

            for k, v in defaults.items():
                setattr(locale_project, k, v)

            locale_project.save()

        return locale_project

    def get_project_slug(self, locale):

        return "%s-%s" % (self.__project_slug_prefix, locale)

    def setup_registry(self):

        registry.registry.setup(
            {
                'http_handler': http_requests.HttpRequest(
                    settings.TRANSIFEX_HOST,
                    auth=auth.BasicAuth(
                        settings.TRANSIFEX_USERNAME,
                        settings.TRANSIFEX_PASSWORD,
                    ),
                ),
            },
        )

    def create_resource(self, slug, lang, name, content,
                        i18n_type=None,
                        project_slug=None):

        resource = resources.Resource(
            project_slug=project_slug or self.get_project_slug(lang),
            slug=str(slug),
        )

        resource.name = name
        resource.i18n_type = i18n_type or DEFAULT_I18N_TYPE
        resource.content = content
        resource.save()

        return resource

    def create_or_update_resource(self, slug, locale, name, content,
                                  i18n_type=None,
                                  project_slug=None):

        resource = self.resource_exists(slug, locale, project_slug=project_slug)
        if not resource:
            return self.create_resource(slug, locale, name, content,
                                        i18n_type=i18n_type,
                                        project_slug=project_slug)
        resource.name = name
        resource.content = content
        resource.save()

        return resource

    def resource_statistics(self, slug, locale, project_slug=None):

        try:
            stats = statistics.Statistics.get(
                project_slug=project_slug or self.get_project_slug(locale),
                resource_slug=slug,
            )
        except NotFoundError:
            stats = None

        return stats

    def delete_resource(self, slug, locale):
        resource = self.resource_exists(slug, locale)
        if resource:
            resource.delete()

    def translation_exists(self, slug, lang, project_slug=None):
        """Return True if the translation exists for this slug."""

        try:
            return translations.Translation.get(
                project_slug=project_slug or self.get_project_slug(lang),
                slug=slug,
                lang=lang,
            )

        except (NotFoundError, RemoteServerError):
            pass

        return False

    def list_resources(self, lang, project_slug=None):
        """Return a sequence of resources for a given lang.

        Each Resource is a dict containing the slug, name, i18n_type,
        source_language_code and the category.
        """
        project_slug = project_slug or self.get_project_slug(lang)
        return registry.registry.http_handler.get(
            '/api/2/project/%s/resources/' % (
                project_slug,)
        )

    def resources(self, lang, slug, project_slug=None):
        """Generate a list of Resources in the Project.

        Yields dicts from the Tx API, with keys including the slug,
        name, i18n_type, source_language_code, and category.

        """

        resource = resources.Resource.get(
            project_slug=project_slug or self.get_project_slug(lang),
            slug=slug,
        )

        return resource

    def resource_exists(self, slug, locale, project_slug=None):
        """Return True if a Resource with the given slug exists in locale."""

        try:
            resource = resources.Resource.get(
                project_slug=project_slug or self.get_project_slug(locale),
                slug=slug,
            )

            return resource

        except NotFoundError:
            pass

        return None
