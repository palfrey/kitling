kitling
-------
[![ci](https://github.com/palfrey/kitling/actions/workflows/ci.yml/badge.svg)](https://github.com/palfrey/kitling/actions)

[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/kitling/comparer?label=docker%3A%20comparer)](https://hub.docker.com/r/kitling/comparer)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/kitling/frontend?label=docker%3A%20frontend)](https://hub.docker.com/r/kitling/frontend)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/kitling/imager?label=docker%3A%20imager)](https://hub.docker.com/r/kitling/imager)

Kitling aka “Moving Kittens as a Service”. It’s a horribly over engineered approach to noticing moving kittens (or any other video feeds you want to hand it).

It consists of a bunch of Docker containers (see the "frontend", "comparer" and "imager" folders) tied together to select the kittens that move the most. Read https://tevps.net/blog/2015/10/29/kitten-videos-an-engineering-approach/ for further information.
