import jwt

INVITE_TOKEN_TYPE_PARTICIPANT = 0
INVITE_TOKEN_TYPE_ADMIN = 1

def create_invite_token(invitation_id, invite_type, token_expiry_days, secret):

    claims = {
        'invitation_id': invitation_id,
        'invitation_type': invite_type,
    }

    return jwt.encode(claims, secret, algorithm='HS256')