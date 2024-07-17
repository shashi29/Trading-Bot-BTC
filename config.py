class Config:
    def __init__(self):
        self.TICKERS = [
    #         "ULTRACEMCO",   # Ultratech Cement
    #         "INFY",        # Dixon
    #         "HAL",          # HAL (Hindustan Aeronautics Limited)
    #         "PERSISTENT",   # Persistent Systems
    #         "DIVISLAB",     # Divis Laboratories
    #         "SIEMENS",      # Siemens
    #         "M&M",           # Mahindra & Mahindra
    #         "LOTUSEYE", "CAREERP", "ONWARDTEC", "AXISTECETF", "NGLFINE", "PILITA", "SONATSOFTW",
    # "PROZONER", "MUKKA", "MEGASTAR", "ITI", "WEALTH", "LAL", "HITECHCORP", "KSOLVES",
    # "XCHANGING", "HARDWYN", "GLS", "KAMOPAINTS", "VINATIORGA", "PIXTRANS", "SBCL", "MON100",
    # "MTNL", "ZENSARTECH"
    #     "LOTUSEYE", "CAREERP", "ONWARDTEC", "AXISTECETF", "NGLFINE", 
    # "PILITA", "SONATSOFTW", "PROZONER", "MUKKA", "MEGASTAR", 
    # "ITI", "WEALTH", "LAL", "HITECHCORP", "KSOLVES", "XCHANGING", 
    # "HARDWYN", "GLS", "KAMOPAINTS", "VINATIORGA", "PIXTRANS", 
    # "SBCL", "MON100", "MTNL", "NDLVENTURE"
    "ongc"
        ]
        
        self.TIME_FRAMES = {
            'TIDE': {'period': '1mo', 'interval': '1d'},
            'WAVE': {'period': '1mo', 'interval': '1h'},
            'RIPPLE': {'period': '1mo', 'interval': '15m'}
        }
        
        self.INDICATORS = {
            'EMA': {
                'period': 50
            },
            'RSI': {
                'window': 14
            },
            'BOLLINGER_BANDS': {
                'period': 20,
                'std_dev': 2
            },
            'DMI': {
                'window': 14
            },
            'STOCHASTIC': {
                'k': 14,
                'd': 3
            }
        }
        
        self.ANALYSIS = {
            'ema_slope_threshold': 0,
            'rsi_threshold': 60,
            'adx_threshold': 15,
            'stochastic_oversold': 20
        }
        
        self.RIPPLE_TIMEFRAMES = ['15m', '1h', '1d', '1w']

    def get_tickers(self):
        return self.TICKERS

    def get_time_frame(self, analysis_type):
        return self.TIME_FRAMES.get(analysis_type.upper(), {})

    def get_indicator_params(self, indicator):
        return self.INDICATORS.get(indicator.upper(), {})

    def get_analysis_param(self, param):
        return self.ANALYSIS.get(param)

    def get_ripple_timeframes(self):
        return self.RIPPLE_TIMEFRAMES


# Singleton instance
config = Config()

# Usage example:
# from config import config
# tickers = config.get_tickers()
# ema_period = config.get_indicator_params('EMA')['period']