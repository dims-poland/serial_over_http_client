import http.client
import logging
import socket
import time
import typing
import urllib.parse

from serial_over_http_client.version import __version__


DEFAULTS = dict(
    host='127.0.0.1',
    port=8888,
    timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
    retry_interval=1,
    num_post_retries=1,
    token_variable='token',
    http_content_type='application/octet-stream',
    logger_name='SerialOverHttpClient',
    token=None
)


class SerialToHttpClientError(RuntimeError):
    pass


class SerialOverHttpClient:

    connection: typing.Union[http.client.HTTPConnection, None]

    @classmethod
    def from_address(
            cls,
            address,
            timeout=DEFAULTS['timeout'],
            retry_interval=DEFAULTS['retry_interval'],
            num_post_retries=DEFAULTS['num_post_retries'],
            token=DEFAULTS['token'],
            token_variable=DEFAULTS['token_variable'],
            http_content_type=DEFAULTS['http_content_type'],
            logger_name=DEFAULTS['logger_name'],
            connect_on_init=True
    ):
        import urllib.parse
        if isinstance(address, str):
            parsed_address = urllib.parse.urlparse(address)
            address = (parsed_address.hostname, parsed_address.port)
        return cls(
            host=address[0],
            port=int(address[1]),
            timeout=timeout,
            retry_interval=retry_interval,
            num_post_retries=num_post_retries,
            token=token,
            token_variable=token_variable,
            http_content_type=http_content_type,
            logger_name=logger_name,
            connect_on_init=connect_on_init,
        )

    def __init__(
            self,
            host=DEFAULTS['host'],
            port=DEFAULTS['port'],
            timeout=DEFAULTS['timeout'],
            retry_interval=DEFAULTS['retry_interval'],
            num_post_retries=DEFAULTS['num_post_retries'],
            token=DEFAULTS['token'],
            token_variable=DEFAULTS['token_variable'],
            http_content_type=DEFAULTS['http_content_type'],
            logger_name=DEFAULTS['logger_name'],
            connect_on_init=True
    ):
        self.connection = None
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.num_post_retries = num_post_retries
        self.token = token
        self.token_variable = token_variable
        self.http_content_type = http_content_type
        self.logger = logging.getLogger(logger_name)
        if connect_on_init:
            self.connect(force=True)
        self._update_token_str()
        self.last_response_data = b''

    def _update_token_str(self):
        if self.token:
            self.token_param_str = '?{}={}'.format(self.token_variable, urllib.parse.quote_plus(self.token))
        else:
            self.token_param_str = ''

    def connect(self, force=True):
        if self.connection is None or force:
            if self.connection is not None:
                try:
                    self.connection.close()
                except:
                    pass
            self.connection = http.client.HTTPConnection(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
        return self.connection

    def read(self):
        last_response_data = self.last_response_data
        self.last_response_data = b''
        return last_response_data

    def readline(self):
        last_response_data = self.last_response_data
        if b'\n' in last_response_data:
            returned = last_response_data[:last_response_data.index(b'\n')+1]
            last_response_data = last_response_data[len(returned):]
        else:
            returned = last_response_data
            last_response_data = b''
        self.last_response_data = last_response_data
        return returned

    def write(self, data):
        if not self.connect():
            # should not happen because connect() should raise an error
            raise SerialToHttpClientError('Cannot connect to the server')
        retries = 0
        request_failed = True
        caught_exc = None
        failure_reason = ''
        while retries < self.num_post_retries or self.num_post_retries < 0:
            try:
                # If headers contains neither Content-Length nor Transfer-Encoding, but there is a request body,
                # one of those header fields will be added automatically
                caught_exc = None
                failure_reason = None
                self.connection.request(
                    method='POST',
                    url=self.token_param_str,
                    body=data,
                    headers={
                        'Content-Length': len(data),
                        'Content-Type': self.http_content_type
                    }
                )
                response = self.connection.getresponse()
                response_data = response.read()
                if response.status == 200:
                    self.last_response_data = response_data
                    request_failed = False
                    break
                else:
                    response_data_decoded = response_data.decode('utf-8')
                    self.logger.error(
                        'Failed to retrieve data - bad response status (HTTP response status: %d. Message: %s.)',
                        response.status,
                        response_data_decoded
                    )
                    failure_reason = f'bad response status. HTTP response status: {response.status}. Message: {response_data_decoded}'
            except Exception as e:
                caught_exc = e
                failure_reason = 'exception'
                self.logger.error(
                    'Failed HTTP request. Exception caught (%s: %s)',
                    e.__class__.__name__, str(e)
                )
                time.sleep(self.retry_interval)
            retries += 1
            time.sleep(self.retry_interval)
            self.connect(force=True)
        # self.num_post_retries > 0 is intentional
        if retries >= self.num_post_retries > 0:
            self.logger.error(f"Too many post attempts (maximum: {self.num_post_retries})")
        if request_failed:
            if caught_exc is not None:
                raise SerialToHttpClientError(f'Request failed due to {failure_reason}') from caught_exc
            else:
                raise SerialToHttpClientError(f'Request failed due to {failure_reason}')

    def close(self):
        if self.connection:
            self.connection.close()

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
