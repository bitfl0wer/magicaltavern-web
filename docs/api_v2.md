# Magicaltavern API Documentation

This document will guide you through the Magicaltavern APIs' Usage, available request routes and
authentication methods.

## Authenticating

Some API routes and request methods are protected. This means, that to use them, you will
have to provide an API key in your request. There currently is no way to generate a new key. You
will have to use a database viewing tool to open `{$PROJECTDIR}/data/db/db.sqlite` and manually
insert a new key in the `devices`-table. The following parameters need to be filled out:

- id: The primary key. A unique integer.
- key: The actual token. Must be unique, and should be URL-safe. UUIDs recommended.
- name: An identifier for the token. Can be anything you'd like.

As a database browsing tool, I recommend [DB Browser for SQLite (Linux, macOS, Windows)](https://sqlitebrowser.org/dl/)

### Properly authenticating

Provide your API key as an attribute named `token` in the requests' header.

### Checking your token

You can check the validity of your token by trying to authenticate under the route `/api/v2.0/auth`.
You will receive a `200 - OK` response if you authenticated correctly.

## Routes

### Authentication

| Route                     | Method | Description                                                                                                                                                                                        | Protected |
|---------------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| /api/v2.0/auth | GET, POST, PUT, DELETE | Check, if your token is valid/if your way of authenticating is correct, as described in [Checking your token](#checking-your-token) | No

### Campaigns

| Route                     | Method | Description                                                                                                                                                                                        | Protected |
|---------------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| /api/v2.0/campaigns       | GET    | Returns all stored campaigns, formatted as .json. The `key` in the `key`-`value`-pair is the campaigns' unique ID.                                                                                 | Yes       |
| /api/v2.0/campaigns       | POST   | Adds a new campaign entry to the database. Data has to be in json-format and located in the request body. The following data needs to be supplied: [Adding a new Campaign](#adding-a-new-campaign) |Yes        |
| /api/v2.0/campaigns/\<campaign_id> | GET    | Returns the campaign which's `key` matches the supplied `id`, formatted as .json.                                                                                                                  | Yes       |
| /api/v2.0/campaigns/\<campaign_id>/allow_enrollment | PUT | Marks the campaign as active for enrollment. This means, that player enrollments via the `/api/v2.0/campaigns/<campaign_id>/players/add/<user_id>` route is accepted, unless the campaign is also marked as finished.                                                                                                               | Yes       |
| /api/v2.0/campaigns/\<campaign_id>/finish | PUT | Marks the campaign as finished. A finished campaign can no longer be modified (read-only). A campaign is intended to be marked as finished, once the last session of the campaign has concluded.                                                                                                              | Yes       |
| /api/v2.0/campaigns/\<campaign_id>/message_id/\<message_id> | PUT | Sets the message_id attribute of the campaign entry. message_id refers to the message that the Discord API Client (magicaltavern-discord) will send to announce a new campaign. This attribute keeps track of the latest message associated with this campaign, which allows for easy deletion and editing of the message.                                                                                                             | Yes       |
| /api/v2.0/campaigns/\<campaign_id>/message_id | GET | Get the message_id attribute of a campaign. | Yes |
| /api/v2.0/campaigns/from_message_id/\<message_id> | GET | Returns the campaign ID of the campaign whose message_id attribute matches the provided message_id parameter. Returns Status Code 400 if the campaign doesn't exist. | Yes |
| /api/v2.0/campaigns/\<campaign_id>/dm | GET | Get the DM of a campaign. Returns User ID. | Yes |
| /api/v2.0/campaigns/\<campaign_id>/dm/add/\<user_id> | PUT | Adds a dm to a campaign. If the User associated with the user_id does not exist, a new user with that ID will be created and elevated to DM privileges. If the User associated with the user_id exists but doesn't have DM privileges, the player will automatically be elevated to DM privileges. Returns HTTP Status Code 201 on success and Status Code 409 if the player already dms this campaign or if the campaign already has a dm.  | Yes |
| /api/v2.0/campaigns/\<campaign_id>/dm/remove/\<user_id> | PUT | Removes a dm from a campaign. If the User associated with the user_id does not exist, a new user with that ID will be created. Returns HTTP Status Code 201 on success and Status Code 409 if the player already doesn't exist in this campaign.  | Yes |
| /api/v2.0/campaigns/\<campaign_id>/players | GET | Get the players of a campaign. Returns a List of User IDs or an empty list. | Yes |
| /api/v2.0/campaigns/\<campaign_id>/players/add/\<user_id> | PUT | Adds a player to a campaign. If the User associated with the user_id does not exist, a new user with that ID will be created. Returns HTTP Status Code 201 on success and Status Code 409 if the player already exists in this campaign.  | Yes |
| /api/v2.0/campaigns/\<campaign_id>/players/remove/\<user_id> | PUT | Removes a player from a campaign. If the User associated with the user_id does not exist, a new user with that ID will be created. Returns HTTP Status Code 201 on success and Status Code 409 if the player already doesn't exist in this campaign.  | Yes |

### Users

| Route                     | Method | Description                                                                                                                                                                                        | Protected |
|---------------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| /api/v2.0/users | GET | Returns all Users as json. The json key is the users discord ID. Includes name and access level. | Yes |
| /api/v2.0/users/\<id> | GET | Returns a User object where User.id == id. Returns status code 400 if the user does not exist. | Yes |
| /api/v2.0/users/\<id>/plays_campaigns | GET | Returns all campaign IDs which the specified User is enrolled in. | Yes |
| /api/v2.0/users/\<id>/dms_campaigns | GET | Returns all campaign IDs which the specified User is a DM of. | Yes |
| /api/v2.0/users/\<user_id>/modify_access/\<access_level>/ | PUT | Modify a users' access Level. The access level is an integer between 0 and 3. See [the User section of the Docs to find out more.](#about-users) | Yes |

Note how adding new users is **not** done through `.../users/`-endpoints. All User Creation happens automatically through the `.../campaigns/`-endpoints. Reason being: This is a glorified Campaign-Player-DM-List. Why would we have a person in our system, who is not enrolled into any campaigns and does not DM any campaigns either?

## PUTting and POSTing Data

### Adding a new Campaign

Adding a new campaign can be done by using the Route defined in [Routes > Campaigns](#campaigns). You can include the following data in the request body:

```json
{
    "name": String,
    "description": String,
    "players_min": int,
    "players_max": int,
    "complexity": int range 0-2,
    "place": String,
    "time": String,
    "content_warnings": String,
    "ruleset": String,
    "campaign_length": int range 0-2,
    "language": int range 0-2,
    "character_creation": String,
    "briefing": String,
    "notes": String,
    "image_url": optional String
}
```

#### Campaign parameters

Most of the parameters, such as name, description, notes etc. should be pretty self-explanatory. However, some parameters require some more explanation. If a parameter isn't specified as "optional", it must be present and have a value in the request body.

**complexity**  
An integer value, ranging from 0-2.

- 0: Easy
- 1: Medium
- 2: Hard

**ruleset**  
A foreign key, which in this case is the primary key of the `ruleset` Table.

**campaign_length**  
An integer value, ranging from 0-2

- 0: Short
- 1: Medium
- 2: Long

**language**  
An integer value, ranging from 0-2

- 0: English
- 1: German
- 2: German and English

**image_url**  
The image URL has to be a direct link to an image.

### About Users

"Users" in the context of this application are unique Discord Accounts. When we talk about a users' ID, what we actually mean is their Discord Account ID. A user has the following attributes:

- id: Discord account id. Integer.
- name: Name of the User Account. Either empty or a String.
- access_level: Integer between 0 and 3. 0 meaning 'Guest', 1 meaning 'Player', 2 meaning 'DM' and 3 meaning 'Admin'.

There are two more attibutes coded into the Database model.

- player_in: Many to Many Relationship of User IDs and Campaign IDs, to keep track of the campaigns a User is enrolled in.
- dm_of: Similar to player_in. Does not keep track of the campaigns a User is enrolled in, but rather what campaigns a User is DM of.

These two attributes require JOIN statements to access and cannot be serialized to JSON using the SerializerMixin.

#### Post-creation

After the campaign has been created, it is recommended to also do the following things, in order:  

1. If a message has been sent by the Discord Bot endpoint (for example to advertise the newly created campaign), set the `message_id` attribute using the corresponding [route](#campaigns).
2. Set the DM attribute, as documented under the campaign routes.
3. If enrollment has concluded/the campaign is full, provide an option to mark the campaign as active.
4. Do not forget to provide an option to mark the campaign as finished.
