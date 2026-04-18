# SureHA 🐾

> **Note:** This is a modified, enhanced, and actively maintained fork of the original SureHA integration. 

## ✨ New Features in this Fork
* **Smart Duration Tracking:** The pet location sensor now includes a `for` attribute (e.g., `1d 04:30` or `02:15`), calculating exactly how long your pet has been inside or outside. No more need for complex Jinja2 templates!
* **Enhanced Battery & Connectivity Stats:** Added exact voltage per cell and formatted RSSI signal strengths for easier debugging of hub connections.

---

## Entities

This project creates the following entities in your Home Assistant instance:

### `sensor.cat_flap`

There will be 1 entity per cat flap with the following attributes:
<details>
  <summary>Click to expand!</summary>
  
  *This is a non-exhaustive list*
  
| Attribute | Example |
|---------------------|-------------------|  
| ID                  | 123456                                                                                                    |
| Parent device ID    | 123456                                                                                                    |
| Product ID          | 6                                                                                                         |
| Household ID        | 123456                                                                                                    |
| Name                | Rivendell                                                                                                 |
| Serial number       | XXXX-XXXXX                                                                                                |
| MAC address         | 2c549188c9e3                                                                                              |
| Index               | 0                                                                                                         |
| Version             | ODM2                                                                                                      |
| Created at          | December 19, 2024, 1:43:25 AM                                                                             |
| Updated at          | December 19, 2024, 1:43:25 AM                                                                             |
| Pairing at          | December 19, 2024, 1:43:25 AM                                                                             |
| Control             | curfew: <br>- enabled:true<br> lock_time:"22:00"<br> unlock_time: "07:30"<br> locking: 0<br> fast_polling:false |
| Parent              | |
| Status              | locking:<br> mode: 0 <br>version:<br> battery: 5.07<br> learn_mode:<br> online:true                       |
| Tags                | |
</details>

### `sensor.cat_flap_battery`

<details>
  <summary>Click to expand!</summary>
  
| Attribute | Example |
|---------------------|-------------------|
| Battery Level       | 85                |
| Voltage             | 5.09              |
| Voltage per battery | 1.27              |
| For                 | 5d 04:12          |
</details>

### `binary_sensor.flap_connectivity` / `binary_sensor.hub`

<details>
  <summary>Click to expand!</summary>

| Attribute   | Example |
|-------------|---------|
| Device rssi | -35.00  |
| Hub rssi    | -42.00  |

</details>

### `binary_sensor.pet`

<details>
  <summary>Click to expand!</summary>

| Attribute                  | Example                                                                |
|----------------------------|------------------------------------------------------------------------|
| **For (Duration)** | **04:25** (Hours:Minutes since last move)                              |
| Since                      | September 18, 2024, 4:09:42 PM                                         |
| Where                      | 1 (Inside) / 2 (Outside)                                               |
| ID                         | 123456                                                                 |
| Name                       | Thorin                                                                 |
| Gender                     | 1                                                                      |
| Comments                   | Such a good cute boy                                                   |
| Household ID               | 123456                                                                 |
| Breed ID                   | 384                                                                    |
| Photo ID                   | 123456                                                                 |
| Version                    | Mg==                                                                   |
| Created at                 | April 1, 2024, 11:00:07 AM                                             |
| Photo                      | id: 238217  <br> location https://surehub.s3.amazonaws.com/...         |
| Status                     | activity:<br> tag_id: 123456 <br>where: 1 <br>since: date              |

</details>


## Services

This project allows you to use the following services in Home Assistant:<br>

### `sureha.set_pet_location`
 
 This service call allows you to update the location of a pet manually. <br>
 Data needed:<br>
   - `pet_id` = this is the surepetcare id for your pet. <br>
   - `where` = options are "Inside" or "Outside"

Example:
```yaml
service: sureha.set_pet_location
data:
  pet_id: 31337
  where: Inside
