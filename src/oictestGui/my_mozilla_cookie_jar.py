from cookielib import LoadError, _warn_unhandled_exception, Cookie
import cookielib
import re, time

__author__ = 'danielevertsson'

class MyMozillaCookieJar(cookielib.MozillaCookieJar):

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()

        magic = f.readline()
        if not re.search(self.magic_re, magic):
            f.close()
            raise LoadError(
                "The cookie does not appear to be in Netscape format. Check that the first line is: <br> # Netscape HTTP Cookie File")

        try:
            while 1:
                line = f.readline()
                if line == "": break
    
                # last field may be absent, so keep any trailing tab
                if line.endswith("\n"): line = line[:-1]

                # skip comments and blank lines XXX what is $ for?
                if (line.strip().startswith(("#", "$")) or
                    line.strip() == ""):
                    continue

                domain, domain_specified, path, secure, expires, name, value = \
                        line.split("\t")
                secure = (secure == "TRUE")
                domain_specified = (domain_specified == "TRUE")
                if name == "":
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # with no name, whereas cookielib regards it as a
                    # cookie with no value.
                    name = value
                    value = None

                initial_dot = domain.startswith(".")
                assert domain_specified == initial_dot

                discard = False
                if expires == "":
                    expires = None
                    discard = True

                # assume path_specified is false
                c = Cookie(0, name, value,
                           None, False,
                           domain, domain_specified, initial_dot,
                           path, False,
                           secure,
                           expires,
                           discard,
                           None,
                           None,
                           {})
                if not ignore_discard and c.discard:
                    continue
                if not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)

        except IOError:
            raise
        except AssertionError:
            raise AssertionError("Cookie does not follow Netscape format. Check that the values only are seperated by tab (\\t)" + self._parse_failed_cookie_message(line))
        except Exception as ex:
            raise Exception(ex.message + self._parse_failed_cookie_message(line))

    def _parse_failed_cookie_message(self, cookie):
        return "<br><br>Failed to load cookie:<br> %r <br>" % (cookie)